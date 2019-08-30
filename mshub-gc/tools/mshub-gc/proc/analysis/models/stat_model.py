# -*- coding: utf-8 -*-
"""
Created on Wed Oct 04 16:08:20 2017

Core module for statistical analysis model handler.

Provides StatisticalModel class.

StatisticalModel class contains methods for statistical model parsing, 
data loading, filtering and preparation for statistical analysis,
results storage in HDF5 format and HTML report generation.
It is designed to provide universal interface between the data and reporting 
on one side and statistical processing methods and libraries on the other.


@author: Dr. Ivan Laponogov
"""

#Importing standard and external modules
import os; 
import sys;
import traceback #This is for displaying traceback in try: except: constructs
import time;

import h5py
import numpy as np
from pandas import isnull;
from sklearn.cluster import KMeans

#If run independently - check system endianness and add path to local modules
if __name__ == "__main__": 
    if sys.byteorder!='little':
        #Use print here instead of printlog as printlog is not yet imported! 
        #The rest should have printlog in place of print.
        print('Only little endian machines currently supported! bye bye ....');
        quit();
    module_path = os.path.abspath('%s/../../..'%os.path.dirname(os.path.realpath(__file__)));
    sys.path.insert(0, module_path); 
    

#Import local/internal modules

#Timing functions for standard stats output
from proc.utils.timing import tic, toc;
from proc.utils.printlog import printlog, LoggingException;
from proc.utils.objectio import store_to_hdf5, restore_from_hdf5;


import proc.io.manageh5db as mh5
from proc.analysis.methods.methods_list import available_stat_analysis_methods;

#Characters allowed in category/group name.
name_characters = set(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_'));

#used palette
color_grey = 0xb3b3b3;
color_green = 0x79d2a6;

def inverted_color(color):
    """
    Provides contrast color to the supplied background color. Used to determine 
    text color given the input background color for table cells in HTML.
    Args: color - int, color (RGB)
    Returns: color - either white for darker backgrounds or black for lighter ones

    """
    r = color % 256;
    g = color // 256 % 256;
    b = color // (256 * 256);
    
    y = ((r * 299) + (g * 587) + (b * 114))/1000;
    if y >= 128:
        return 0;
    else:
        return 0xFFFFFF;

def get_random_color(valueset):
    """
    Generate a list of soft random colors given the list of values.
    
    Args: valueset - list of values to generate random colors for. 
    
    Returns: dictionary of colors with keys being values from valueset.
    
    """
    result = {};
    v = np.random.randint(150, 255, size = (len(valueset), 3));
    v[:, 1] = v[:, 1] * 256;
    v[:, 2] = v[:, 2] * 256 * 256;
    c = np.sum(v, axis = 1);
    for i in range(len(valueset)):
        result[valueset[i]] = c[i];
    return result;


#Exception class for stat. model parsing errors
class ParseError(LoggingException):
    pass

#Exception class for parameter errors
class ParameterError(LoggingException):
    pass



#General token class for stat. model string representation parsing
#Is not meant to be used outside of the module
class Token(object):
    token_description = 'BaseToken';
    
    def __init__(self, data, parent = None): #data - value of the token data, parent - parent token
        self.data = data;
        self.set_parent(parent);
        self.sign = 1; #set sign of the token to +1 by default.

    def set_sign(self, sign): #set and recursively update the sign in children tokens
        self.sign = self.sign * sign;
        if isinstance(self.data, list):
            for i in self.data:
                if isinstance(i, Token):
                    i.set_sign(sign);
        
    def __repr__(self): #Generate text representation of the token recursively
        result = '\t' * self.level + self.token_description + ': ' + str(self.sign) + ' ';
        if isinstance(self.data, list):
            for d in self.data:
                if isinstance(d, Token):
                    result += '\n%s'%str(d);
                else:
                    result += '\n' + ('\t' * (self.level + 1)) + str(d);
        else:
            result += str(self.data)
        return result
        
    def set_parent(self, parent = None): #Set parent and propagate parent information to children tokens. Also recursively update depth level

        self.parent = parent;

        if not parent is None:
            self.level = parent.level + 1;
        else:
            self.level = 0;
       
        if isinstance(self.data, list):
            for d in self.data:
                if isinstance(d, Token):
                    d.set_parent(self);
    
    def get_string(self): #Get sting representation of the data of this token
        return str(self.data)

class BracketsToken(Token): #Token holding brackets
    token_description = 'Brackets';
    def get_string(self):
        ss = [];
        for d in self.data:
            ss.append(d.get_string())
        return '('+''.join(ss)+')';

class NameToken(Token):#Token for name entities
    token_description = 'Name';
    def get_string(self):
        return str(self.data);

class CategoryToken(Token):#Token for categories, e.g. C(dose) or C(time)
    token_description = 'Category';
    def get_string(self):
        return 'C('+str(self.data)+')';
    

class OperatorToken(Token):#Token for operators, incl. '+', '-', ':', '*'
    operator_sign = 'Operator';
    token_description = 'OperatorToken';
    def get_string(self):
        return self.data[0].get_string() + self.operator_sign + self.data[1].get_string();
    

class DeepCrossToken(OperatorToken):
    # Token for interaction with all individual combinations also considered (crossing). 
    #'*' in R notation: C(drug)*C(dose) == C(drug) + C(dose) + C(drug):C(dose)
    operator_sign = '*';
    token_description = 'DeepCross';

class CrossToken(OperatorToken):
    # Token for interaction, ':' in R notation: C(drug):C(dose)
    operator_sign = ':';
    token_description = 'Cross';
    def get_string(self):
        s1 = self.data[0].get_string();
        s2 = self.data[1].get_string();
        if isinstance(self.data[0], AddToken) or isinstance(self.data[0], SubtractToken):
            s1 = '(' + s1 + ')';
        if isinstance(self.data[1], AddToken) or isinstance(self.data[1], SubtractToken):
            s2 = '(' + s2 + ')';
        return s1 + self.operator_sign + s2;
        
class AddToken(OperatorToken): #Token for addition operation '+'
    operator_sign = '+';
    token_description = 'Add';

class SubtractToken(OperatorToken): #Token for subtraction operation '-'
    operator_sign = '-';
    token_description = 'Subtract';
    def get_string(self):
        s1 = self.data[0].get_string();
        s2 = self.data[1].get_string();
        
        if isinstance(self.data[1], AddToken) or isinstance(self.data[1], SubtractToken):
            s2 = '(' + s2 + ')';
        return s1 + self.operator_sign + s2;
        
        
class CombinationToken(Token): #Token to hold individual categories or their combinations defined by ':' operators, e.g. C(dose):C(drug):C(age)
    token_description = 'Combination';
        
    def get_string(self):
        results = [];
        for i in self.data:
            results.append('C(' + i + ')');
        
        if self.sign > 0:
            return '{' + ':'.join(results) + '}';
        else:
            return '{-' + ':'.join(results) + '}';
        
        
def tokens_to_str(tokens): #get text representation of token tree
    s = [];
    for token in tokens:
        s.append(str(token));
    
    return '\n'.join(s);

def tokens_to_str_line(tokens): #print a list of tokens
    for t in tokens:
        print(t.get_string())
        
        
class StatisticalModel(object):
    """
    The main class for statistical model handling, data preparation, results 
    aggregation and storage and final report generation.
    Once instantiated with the necessary input parameters call
    analyse_by_method(self, method_name, methodparams) method to perform the 
    analysis. To avoid confusions, use this method only once per instance of the
    StatisticalModel class.
    
    """
    

    def __init__(self, 
                 model, 
                 groupingparams,
                 h5file, 
                 h5readpath, 
                 h5writepath, 
                 dataset_names, 
                 dataset_indeces, 
                 rt_indeces, 
                 report_path, 
                 output_prefix_with_path):
        """
        Initialize StatisticalModel instance.
        Args: model - text representation of the statistical model in R notation. Currently only categorical values are supported and
                      operators such as '+', '-', ':', and '*'. Example: 'C(dose)*C(drug)*C(date)-C(drug)*C(date)'. Brackets of any level
                      and complexity are supported.
              groupingparams - dictionary containing grouping parameters. 'n_groups' - number of groups to group results into by KMeans,
                              'group_by' - list of result categories to group by (e.g. 'p_value_threshold'), group_weights - list of corresponding 
                              weights for grouping factors.
                              
              h5file - hdf5 file open for reading and writing and containing your data to be analysed.
              h5readpath - absolute path to the datasets to be processed by statistical analysis. Must contain quantity integrals and metadata
              h5writepath - absolute path in the group in HDF5 to store results into
              dataset_names - list of dataset names to use in stat. analysis
              dataset_indeces - list of corresponding dataset indeces in combined quantity_integrals dataset in h5readpath
              rt_indeces - list of indeces of rt peaks to be covered by the analysis
              report_path - absolute path to the folder where the report should be written to
              output_prefix_with_path - absolute path to the report folder combined with the report name prefix.
              

        """             
        #Store supplied parameters             
        self.source_model = model;
        self.h5file = h5file;
        self.h5readpath = h5readpath;
        self.h5writepath = h5writepath;
        self.dataset_names = dataset_names;
        self.dataset_indeces = dataset_indeces;
        self.rt_indeces = rt_indeces;
        self.report_path = report_path;
        self.output_prefix_with_path = output_prefix_with_path;
        self.groupingparams = groupingparams;
        self._checkgroupingparams(); #Verify grouping parameters and update as needed.
        self._parse_model(); #Parse statistical model
        self._filter_samples();#Filter samples according to available metadata and parsed model
        
        
        
    def _checkgroupingparams(self):
        #Verify that grouping parameters supplied are valid
        #Unpack the parameters
        self.groups = self.groupingparams['group_by'];
        self.group_weights = self.groupingparams['group_weights'];
        self.n_groups = self.groupingparams['n_groups'];
        
        #Number of groups and number of group weights should match unless the group weight is 1.0 - in this case it is applied to all groups.        
        if isinstance(self.group_weights, float) and self.group_weights == 1.0:
            self.group_weights = [1.0] * len(self.groups);
        elif isinstance(self.group_weights, float) and self.group_weights != 1.0 and len(self.groups) == 1:
            self.group_weights = [self.group_weights];
        elif isinstance(self.group_weights, float) and self.group_weights != 1.0 and len(self.groups) > 1:    
            raise ParameterError('Error in input parameters! Number of groups and number of group weights do not match!\ngroups: %s\nweights: %s '%(self.groups, self.weights));
        elif len(self.group_weights) != len(self.groups):
            raise ParameterError('Error in input parameters! Number of groups and number of group weights do not match!\ngroups: %s\nweights: %s '%(self.groups, self.weights));
        
        
        #Prepare group_and_weights dictionary for storage of groups with their corresponding weights. Used for fast group weight lookup.
        self.group_and_weights = {};
        for i in range(len(self.groups)):
            self.group_and_weights[self.groups[i]] = self.group_weights[i];
        #if not self.group_distance_function in self.supported_grouping_functions:
        #    raise ParameterError('Error in input parameters! Unsupported group distance function %s! Supported functions: %s'%(self.group_distance_function, self.supported_grouping_functions));
        
        
    @staticmethod
    def _dequote(tokens): #Parse quotes in stat model definition
        in_quotes = False;
        quote_char = '';
        quote_string = '';
        start_index = -1;
        
        i = -1;
        
        while i < len(tokens) - 1 :
            i += 1;
            c = tokens[i];
            if in_quotes:
                if c == quote_char:
                    in_quotes = False;
                    tokens[start_index] = NameToken(quote_string);
                    del tokens[start_index + 1 : i + 1];
                    i = start_index + 1;
                else:
                    quote_string += c;
                    
            elif c == '"' or c == "'":
                start_index = i;
                quote_string = '';
                quote_char = c;
                in_quotes = True;
                
        if in_quotes:
            raise ParseError('Error! No closing quote found! : %s'%tokens_to_str(tokens));


    @staticmethod
    def _get_inside_brackets(tokens, closing_bracket): #Parse brackets in stat model definition recursively
        i = -1;
        offset = 0;
        while i < len(tokens) - 1 :
            i += 1;
            c = tokens[i];
            if not isinstance(c, Token):
                if c == '(' or c == '{' or c == '[':
                    if c == '(':
                        closing_bracket = ')';
                    elif c == '{':
                        closing_bracket = '}';
                    else:
                        closing_bracket = ']';
                    inside_brackets, closing_index = StatisticalModel._get_inside_brackets(tokens[i+1:], closing_bracket);
                    tokens[i] = inside_brackets;

                    del tokens[i + 1 : i + closing_index + 2];
                    
                    offset += closing_index + 1;
                    
                elif c == closing_bracket:
                    return BracketsToken(tokens[0:i]), i + offset;
                    
                elif c == ')' or c == '}' or c == ']':
                    raise ParseError('Closing bracket "%s" without matching opening bracket in %s!'%(c, tokens_to_str(tokens)));
        
        raise ParseError('Closing bracket "%s" not found in %s !'%(closing_bracket, tokens_to_str(tokens)))

        
    @staticmethod    
    def _debracket(tokens): #Prepare and call recursive brackets parsing
        tokens.append(')');
        inside_brackets, closing_index = StatisticalModel._get_inside_brackets(tokens[0:], ')');
        tokens[0] = inside_brackets;
        del tokens[1:];
        
    
    @staticmethod        
    def _despace(tokens): #Remove empty space separators such as space, tab etc.
        for i in reversed(range(len(tokens))):
            if not isinstance(tokens[i], Token):
                if tokens[i] in (' ','\t', '\n', '\r'):
                    del tokens[i]
                    
    @staticmethod                        
    def _name_condense(tokens): #Collect individual letters into names recursively
        in_name = False;
        name_string = '';
        start_index = -1;
        i = -1;
        while i < len(tokens) - 1 :
            i += 1;
            c = tokens[i];
            if in_name:
                if isinstance(c, Token) or (not c in name_characters):
                    in_name = False;
                    tokens[start_index] = NameToken(name_string);
                    del tokens[start_index + 1 : i];
                    i = start_index + 1;
                else:
                    name_string += c;
            else:
                if (not isinstance(c, Token)) and (c in name_characters):
                    in_name = True;
                    name_string = c;
                    start_index = i;
        
        if in_name:    
            tokens[start_index] = NameToken(name_string);
            del tokens[start_index + 1 :];
        
    @staticmethod
    def _modelset(tokens): #Identify categories, e.g. C(dose), C(date)
        i = -1;
        while i < len(tokens) - 1 :
            i += 1;
            token = tokens[i]
            
            if isinstance(token, NameToken):
                if token.data == 'C':
                    if i < len(tokens) - 1:
                        next_token = tokens[i + 1];

                        if not isinstance(next_token, BracketsToken):
                            raise ParseError('No brackets after category definition! %s'%tokens_to_str(tokens));

                        if len(next_token.data) > 1:
                            raise ParseError('More than one object in category name! %s in %s'%(next_token.data, tokens_to_str(tokens)));
                                
                        if len(next_token.data) == 0:
                            raise ParseError('No object in category name! %s'%(tokens_to_str(tokens)));    
                                
                        category = next_token.data[0];

                        if not isinstance(category, Token):
                            raise ParseError('Unknown entity in category name! %s in %s'%(category, tokens_to_str(tokens)));

                        if isinstance(category, NameToken):
                            parent = token.parent;
                            tokens[i] = CategoryToken(category.data, parent);
                            del tokens[i + 1];
                        else:
                            raise ParseError('Wrong category name definition! %s in %s. \nOnly the following symbols allowed in category names: %s'%(category, tokens_to_str(tokens), ''.join(name_characters)));
                    else:
                        raise ParseError('Category definition without category! %s'%tokens_to_str(tokens))
                            
            elif isinstance(token, BracketsToken):
                    StatisticalModel._modelset(token.data);
                    
    @staticmethod
    def _operationset(tokens, token_operators, token_classes, parent = None): #Identify operators, such as '+', '-', '*', ':'
        i = -1;
        while i < len(tokens) - 1 :
            i += 1;
            token = tokens[i]
            if not isinstance(token, Token):
                if token in token_operators:
                    op_index = token_operators.index(token);
                    
                    if i < 1 :
                        raise ParseError('Missing left argument of "%s" operator! %s'%(token_operators[op_index], tokens_to_str(tokens)));
                    if i > len(tokens) - 2:
                        raise ParseError('Missing right argument of "%s" operator! %s'%(token_operators[op_index], tokens_to_str(tokens)));
                        
                    prev_token = tokens[i - 1];

                    if not (isinstance(prev_token, CategoryToken) or isinstance(prev_token, BracketsToken) or isinstance(prev_token, OperatorToken)):
                             raise ParseError('Invalid left argument of "%s" operator! %s'%(token_operators[op_index], tokens_to_str(tokens)));
                        
                    post_token = tokens[i + 1];
                    
                    if not (isinstance(post_token, CategoryToken) or isinstance(post_token, BracketsToken) or isinstance(post_token, OperatorToken)):
                             raise ParseError('Invalid right argument of "%s" operator! %s'%(token_operators[op_index], tokens_to_str(tokens)));

                    if isinstance(prev_token, BracketsToken) or isinstance(prev_token, OperatorToken):
                        StatisticalModel._operationset(prev_token.data, token_operators, token_classes, prev_token);

                    if isinstance(post_token, BracketsToken) or isinstance(post_token, OperatorToken):
                        StatisticalModel._operationset(post_token.data, token_operators, token_classes, post_token);

                    i -= 1;
                                        
                    tokens[i] = token_classes[op_index]([prev_token, post_token], parent);
                    del tokens[i + 1: i + 3];
            
            elif isinstance(token, BracketsToken):
                StatisticalModel._operationset(token.data, token_operators, token_classes, token);

    @staticmethod            
    def _check_unparsed(tokens): #Check if any tokens are yet unidentified
        for token in tokens:
            if not isinstance(token, Token):
                raise ParseError('Unknown token "%s" found in %s!'%(token, tokens_to_str(tokens)));
            else:
                if isinstance(token, BracketsToken):
                    StatisticalModel._check_unparsed(token.data);
                elif not (isinstance(token, OperatorToken) or (isinstance(token, CategoryToken) and len(tokens) == 1)):
                    raise ParseError('Orfan tokens present in %s!'%tokens_to_str(tokens));


    @staticmethod
    def _evaluate_deepcross(tokens): #Recursively expand '*' operator
        for i in range(len(tokens)):
            token = tokens[i];
            if isinstance(token, BracketsToken):
                StatisticalModel._evaluate_deepcross(token.data);
            elif isinstance(token, DeepCrossToken):
                parent = token.parent;
                StatisticalModel._evaluate_deepcross(token.data);
                v1 = token.data[0];
                v2 = token.data[1];
                v1v2 = CrossToken([v1,v2]);
                s1 = AddToken([v1, v2]);
                tokens[i] = AddToken([s1, v1v2], parent);
            elif isinstance(token, OperatorToken):
                StatisticalModel._evaluate_deepcross(token.data);
                
    @staticmethod
    def _evaluate_brackets(tokens):      #expand brackets recursively          
        for i in range(len(tokens)):
            token = tokens[i];
            if not isinstance(token, CategoryToken):
                StatisticalModel._evaluate_brackets(token.data);
            if isinstance(token, BracketsToken):
                if len(token.data) == 1:
                    parent = token.parent;
                    token = token.data[0];
                    tokens[i] = token;
                    tokens[i].set_parent(parent);
                else:
                    raise ParseError('More than one token in brackets after parsing!')
            
    @staticmethod
    def _evaluate_cross(tokens):                #Recursively expand cross operator ':', e.g. C(dose):(C(date)+C(patient)) => C(dose):C(date)+C(dose):C(patient)
        for i in range(len(tokens)):
            token = tokens[i];
            if isinstance(token, CrossToken):
                if isinstance(token.data[0], AddToken) or isinstance(token.data[0], SubtractToken):
                    parent = token.parent;
                    s1 = token.data[0].data[0];
                    s2 = token.data[0].data[1];
                    v2 = token.data[1];
                    c1 = CrossToken([s1, v2]);
                    c2 = CrossToken([s2, v2]);
                    tokenclass = token.data[0].__class__;
                    token = tokenclass([c1, c2], parent);
                    tokens[i] = token;
                    
                elif isinstance(token.data[1], AddToken) or isinstance(token.data[1], SubtractToken):                    

                    parent = token.parent;
                    s1 = token.data[1].data[0];
                    s2 = token.data[1].data[1];
                    v2 = token.data[0];
                    c1 = CrossToken([s1, v2]);
                    c2 = CrossToken([s2, v2]);
                    tokenclass = token.data[1].__class__;
                    token = tokenclass([c1, c2], parent);
                    tokens[i] = token;
                    
            if not isinstance(token, CategoryToken):
                StatisticalModel._evaluate_cross(token.data);
                
    @staticmethod                
    def _evaluate_uniquecombinations(tokens): #Recursively replace combinations (e.g. C(dose):C(date):C(patient)) with CombinationToken(e.g.[dose,date,patient])
        for i in range(len(tokens)):
            token = tokens[i];

            if not (isinstance(token, CategoryToken) or isinstance(token, CombinationToken)):
                StatisticalModel._evaluate_uniquecombinations(token.data);

            if isinstance(token, CrossToken):
                parent = token.parent;
                d1 = token.data[0];
                d2 = token.data[1];
                
                if isinstance(d1, CategoryToken):
                    v1 = [d1.data];
                elif isinstance(d1, CombinationToken):
                    v1 = list(d1.data);
                else:
                    raise ParseError('Inappropriate Token %s'%str(d1));

                if isinstance(d2, CategoryToken):
                    v2 = [d2.data];
                elif isinstance(d2, CombinationToken):
                    v2 = list(d2.data);
                else:
                    raise ParseError('Inappropriate Token %s'%str(d2));
                
                tokens[i] = CombinationToken(frozenset(v1+v2), parent);
                tokens[i].sign = 1;
                
            elif isinstance(token, CategoryToken):
                tokens[i] = CombinationToken(frozenset([token.data]), token.parent);
                tokens[i].sign = 1;

    @staticmethod                
    def _evaluate_negation(tokens): #Evaluate negations recursively
        for i in range(len(tokens)):
            token = tokens[i];
            if isinstance(token, SubtractToken):
                d1 = token.data[0];
                d2 = token.data[1];
                d2.set_sign(-1);
                token = AddToken([d1, d2], token.parent);
                tokens[i] = token;
            if not isinstance(token, CombinationToken):
                StatisticalModel._evaluate_negation(token.data);
                
    @staticmethod                    
    def _evaluate_positive(tokens): #Combine positive combination tokens recursively
        result = [];
        for token in tokens:
            if isinstance(token, CombinationToken):
                if token.sign > 0:
                    result.append(token.data);
            else:
                result += StatisticalModel._evaluate_positive(token.data);
        
        return result;
        
        
    @staticmethod                    
    def _evaluate_negative(tokens): #Combine negative combination tokens recursively
        result = [];
        for token in tokens:
            if isinstance(token, CombinationToken):
                if token.sign < 0:
                    result.append(token.data);
            else:
                result += StatisticalModel._evaluate_negative(token.data);
        
        return result;
        
                        
    def _parse_model(self): #Parsing stat. model
    
        printlog('Parsing model: %s'%self.source_model);
        tokens = list(self.source_model); #convert input string into the list of characters
        StatisticalModel._dequote(tokens); #convert enquoted parts of the string into Name tokens, 
        #e.g. ['"','H','e','l','l','o','"'] => [NameToken('Hello')]
        StatisticalModel._name_condense(tokens); #Condense individual letters into Name tokens where appropriate, 
        #e.g.['H','e','l','l','o','+','C'] =>[NameToken('Hello'),'+',NameToken('C')]
        StatisticalModel._despace(tokens);#Remove spaces, 
        #e.g. [NameToken['Hello'],' ',' ',' ',NameToken['world']] => [NameToken['Hello'],NameToken['world']]
        StatisticalModel._debracket(tokens);#Detect brackets, 
        #e.g. ['(',NameToken['Hello'],')'] => [BracketsToken[NameToken['Hello']]]
        StatisticalModel._modelset(tokens);#Detect C(dose) like constructs, 
        #e.g. [NameToken['C'], BracketsToken[NameToken['dose']]] => [CategoryToken['dose']]
        StatisticalModel._operationset(tokens, ['*'], [DeepCrossToken]); #Detect operator '*', 
        #e.g. [CategoryToken['dose'],'*',CategoryToken['time']] => [DeepCrossToken[CategoryToken['dose'],CategoryToken['time']]]
        StatisticalModel._operationset(tokens, [':'], [CrossToken]); #Detect operator ':', 
        #e.g. [CategoryToken['dose'],':',CategoryToken['time']] => [CrossToken[CategoryToken['dose'],CategoryToken['time']]]
        StatisticalModel._operationset(tokens, ['+', '-'], [AddToken, SubtractToken]); #Detect operators '+' and '-', 
        #e.g. [CategoryToken['dose'],'+',CategoryToken['time']] => [AddToken[CategoryToken['dose'],CategoryToken['time']]]
        StatisticalModel._check_unparsed(tokens);#Check if there are any left-over unparsed tokens. 
        #Only BracketsToken, CategoryToken and OperatorToken should remain at this stage
        StatisticalModel._evaluate_deepcross(tokens);#Expand '*' operator, 
        #e.g. [DeepCrossToken[CategoryToken['drug'], CategoryToken['date']]] => [AddToken[
        #                                                                                  AddToken[CategoryToken['drug'],CategoryToken['date']],
        #                                                                                  CrossToken[CategoryToken['drug'],CategoryToken['date']]          
        #                                                                                  ]]
        #or C(drug)*C(date) => C(drug)+C(date)+C(drug):C(date)
        StatisticalModel._evaluate_brackets(tokens); #At this point in brackets we will either have OperatorToken or CategoryToken, so brackets can be removed, e.g.
        #[BracketsToken[CategoryToken['drug']]] => [CategoryToken['drug']]
        StatisticalModel._evaluate_cross(tokens); #Evaluate CrossTokens containing deeper OperatorTokens, e.g.
        #e.g. C(drug):(C(dose)+C(patient)) => C(drug):C(dose)+C(drug):C(patient)
        StatisticalModel._evaluate_uniquecombinations(tokens);# Convert each individual CategoryToken and each combination of CrossTokens into one CombinationToken
        #e.g. CrossToken[CategoryToken['drug'],CrossToken[CategoryToken['date'],CategoryToken['patient']]] => CombinationToken['drug','date','patient']
        #for C(drug):C(date):C(patient)
        StatisticalModel._evaluate_negation(tokens); #Evaluate negative signs, e.g.
        #C(patient)-(C(drug)-C(dose)) => C(patient) + C(-drug) + C(dose)
        positive = StatisticalModel._evaluate_positive(tokens); #Group positive tokens:
        #['patient', 'dose']. Combinations are uniqualized, i.e. C(dose):C(drug) == C(drug):C(dose)
        negative = StatisticalModel._evaluate_negative(tokens); #Group negative tokens:
        #['drug']
        
        self.combinations = list(set(positive) - set(negative)); #Exclude negative tokens from positive token set
        
        categories = [];
        for i in range(len(self.combinations)):
            combination = list(self.combinations[i]);
            categories += combination;
            self.combinations[i] = combination;
        
        #self.combinations stores a list of unique combinations of categories as lists,
        #e.g. [['dose'], ['time'], ['dose', 'time']]
        
        #Stores the list of unique entries of categories, 
        #e.g. ['dose', 'time', 'patient']
        self.unique_categories = list(set(categories)); 
        
        combistring = [];
        for combination in self.combinations:
            combistring.append('C('+'):C('.join(combination)+')');
            
        self.model_clean = combistring;
        #self.model_clean contains the re-constructed model definition, e.g.
        #C(dose)+C(drug)+C(dose):C(drug)
        
        printlog('\nUnique categories to be considered by the model: \n%s'%(','.join(self.unique_categories)));
        printlog('\nCombinations to be considered by the model: \n%s'%('\n'.join(combistring)));
        
                
        
        
    def _filter_samples(self):
        printlog('\nFiltering samples according to available metadata...');
        printlog('Initial number of selected samples: %s'%len(self.dataset_names));

        #Get True/False masks for datasets based on the presence of the corresponding metadata values for stat. model categories        
        self.dataset_categories = [];
        for i in range(len(self.dataset_names)):
            self.dataset_categories.append(mh5.has_metadata_entries(self.h5file, self.h5readpath, self.dataset_names[i], self.unique_categories));

        self.selected_datasets = [];
        self.selected_dataset_indeces = [];
        
        for i in range(len(self.dataset_names)):
            if not (False in self.dataset_categories[i]):
                self.selected_datasets.append(self.dataset_names[i]);
                self.selected_dataset_indeces.append(self.dataset_indeces[i]);
        

        self.selected_dataset_indeces = np.array(self.selected_dataset_indeces);
        printlog('Final number of selected samples: %s'%len(self.selected_datasets))

        #self.selected_datasets - list of datasets for which all the needed metadata is found. If any category is missing in the metadata,
        #the corresponding sample is ignored.
        #self.selected_dataset_indeces - corresponding NumPy array of dataset indeces for the quantity_integrals array slicing.
        
        self._prepare_metadata(); #Load metadata for selected datasets

        
            

    def analyse_by_method(self, method_name, methodparams):
        """
        Performs statistical analysis of the data
        Args: method_name - name of the statistical method to be used from the list
                            of available methods.
              methodparams - corresponding method parameters in the form of a dictionary
              
              To avoid confusion and overwriting the results, this method is intended 
              to be called once per each instance of StatisticalModel
        
        """
        
        self.method_name = method_name; #Set and check method name
        if not method_name in available_stat_analysis_methods:
            printlog('%s method not found among implemented methods: \n%s !'%(method_name, '\n'.join(available_stat_analysis_methods.keys())));
            return
        
        rts_set = self.h5readpath + '/grouped_rts'; #find grouped_rts dataset in hdf5
        if not (rts_set in self.h5file):
            raise mh5.H5FileError('Error! grouped_rts not found in [%s]%s !'%(self.h5file.filename, self.h5readpath));
    
        self.rts = self.h5file[rts_set]; #self.rts holds grouped_rts dataset from hdf5
        
        self.selected_rts = np.array(self.rts)[self.rt_indeces]; #self.selected_rts  holds only selected rt values according to self.rt_indeces 
        
        quantity_integrals_set = self.h5readpath + '/quantity_integrals'; #find quantity_integrals array in hdf5
        if not (quantity_integrals_set in self.h5file):
            raise mh5.H5FileError('Error! quantity_integrals not found in [%s]%s !'%(self.h5file.filename, self.h5readpath));
        
        self.quantity_integrals = self.h5file[quantity_integrals_set]; #self.quantity_integrals holds corresponding dataset in open hdf5
        
        self._initialize_reporting(); #Prepare for report generation
        
        self.all_dataset_names, self.all_indeces = mh5.get_dataset_names_from_hdf5(self.h5file, self.h5readpath, return_indeces = True); #Load full list of available datasets in HDF5
        
        self.sel_sets = set(self.selected_dataset_indeces); #set of only selected dataset indeces
        self._generate_sample_selection_report();   #HTML report showing selected rts and datasets vs all available rts and datasets in HDF5         
        self._generate_group_selection_report(); #HTML report showing selected groups from metadata according to the stat. model specified
        self._generate_metamodel_selection_report();#HTML report showing all combinations of categories of metadata according to stat. model selection
        
        Stat_Method = available_stat_analysis_methods[method_name]; #Get stat method class by name
        stat_method_instance = Stat_Method(self, methodparams); #Instantiate it
        stat_method_instance.analyse(); #Do analysis
        
        self._group_results(); # Group results by KMeans
        self._generate_stat_report(); #Generate report for statistical analysis       
        self._finalize_report(); #Finalize report generation
        

    def _prepare_metadata(self): #Prepare extracted metadata for use
        printlog('\nExtracting metadata...');
        
        #self.meta_data is a list of lists. Top level list corresponds to categories from self.unique_categories
        #inner lists correspond to metadata values for these categories from selected samples.
        self.meta_data = [];
        uc_count = len(self.unique_categories);
        for i in range(uc_count):
            self.meta_data.append([]);

        for dataset_name in self.selected_datasets:
            metapath = self.h5readpath + '/' + dataset_name + '/MetaData';
            metagroup = self.h5file[metapath];
            for i in range(uc_count):
                self.meta_data[i].append(metagroup.attrs[self.unique_categories[i]]);
        
        self.combination_data = [];
        self.combination_color = [];
        self.unique_subsets = [];
        self.unique_subsets_color = [];
        self.unique_subsets_count = [];
        
        #self.meta_data_dictionary contains metadata lists for each category for 
        #speedy access by category name, i.e. metadata = self.meta_data_dictionary[category]
        self.meta_data_dictionary = {};
        for i in range(len(self.unique_categories)):
            self.meta_data_dictionary[self.unique_categories[i]] = self.meta_data[i];

        
        for i in range(len(self.combinations)):
            c = set(self.combinations[i]);
            combination = [];
            counts = {};
            for k in range(len(self.selected_datasets)):
                cc = [];
                for j in range(uc_count):
                    if self.unique_categories[j] in c:
                        cc.append(self.meta_data[j][k]);
                combination.append(tuple(cc));

            subs = list(set(combination));
            self.unique_subsets.append(subs);
            self.unique_subsets_color.append(get_random_color(subs));

            self.combination_data.append(combination);
            self.combination_color.append([0] * len(self.selected_datasets));
            
            for j in range(len(subs)):
                r = subs[j];
                counts[r] = 0;
                for k in range(len(combination)):
                    if combination[k] == r:
                        counts[r] += 1;
                        self.combination_color[-1][k] = self.unique_subsets_color[-1][combination[k]];
                #counts.append(c);
            self.unique_subsets_count.append(counts);
        
        #print(self.unique_subsets)
        #print(self.combination_data)
        #raise TypeError('stop')
        
            
    def _initialize_reporting(self):
        #create output folder for HTML report using self.output_prefix_with_path if not available 
        #initialize two lists: self.html_titles and self.html_filenames. 
        #These ones are populated by the methos generating individual reports 
        #and contain titles and filenames (with relative path) of individual reports respectively.
        #They will be used to generate the list of available individual reports at the end
        if not os.path.exists(self.output_prefix_with_path):
            os.makedirs(self.output_prefix_with_path);
            
        self.html_titles = [];    
        self.html_filenames = [];



    def _generate_metamodel_selection_report(self):
        #HTML report showing all combinations of categories of metadata according to stat. model selection
        printlog('\nGenerating model and metadata selection report...');
        
        with open(os.path.join(self.output_prefix_with_path, 'sample_model.html'), 'w') as fout:
            fout.write('\n'.join([
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<title>Selected samples & MetaData groups</title>',
                '</head>',
                '<body>',]));
                
            fout.write('\n'.join([
                '<h1>Selected samples & MetaData groups</h1>', 
                ]))   
                
            meta_string = [];
            #Generate table header containing category combinations
            for i in range(len(self.combinations)):
                meta_string.append('<th>%s</th>'%(
                '<font style="color:black;">C(</font><font style="color:blue;">' 
                + 
                '</font><font style="color:black;">)<font style="color:red;">:</font>C(</font><font style="color:blue;">'.join(self.combinations[i]) 
                + 
                '</font><font style="color:black;">)</font>'));
                
            fout.write('\n'.join([
                '    <table border=1>',
                '    <tr><th>Sample</th>',
                ''.join(meta_string),
                '</tr>',
                ]));
            #Populate table with category data combinations with corresponding colors    
            for i in range(len(self.selected_datasets)):
                meta_string = [];
                
                for j in range(len(self.combinations)):
                    data = self.combination_data[j][i];
                    color = self.combination_color[j][i];
                    strdata = [];
                    for d in data:
                        strdata.append(str(d));
                    
                    meta_string.append('<td bgcolor="#%06x"><font color="#%06x">%s</font></td>'%(color, inverted_color(color), '*'.join(strdata)));
                    
                fout.write('\n'.join([
                '    <tr><td>%s</td>'%self.selected_datasets[i],
                ''.join(meta_string),
                '</tr>',
                ]))
                
            #Generate individual tables per combination with statistics    
            fout.write('\n'.join([                
                '    </table>',
                '<h1>Unique groups and corresponding sample counts</h1>', 
                ]));
                
            for i in range(len(self.combinations)):

                fout.write('\n'.join([
                    '<h2><font style="color:black;">C(</font><font style="color:blue;">'
                    + 
                    '</font><font style="color:black;">)<font style="color:red;">:</font>C(</font><font style="color:blue;">'.join(self.combinations[i]) 
                    + 
                    '</font><font style="color:black;">)</font></h2>',
                    '    <table border=1>',
                    '    <tr><th>Combination</th><th>Sample Count</th></tr>',
                    ]));

                for j in range(len(self.unique_subsets[i])):
                    subset = self.unique_subsets[i][j];
                    #print(subset)
                    color = self.unique_subsets_color[i][subset];
                    #print(color)
                    dcount = self.unique_subsets_count[i][subset];
                    #print(dcount)
                    strdata = [];
                    for d in subset:
                        strdata.append(str(d));
          
                    comb = '<td bgcolor="#%06x"><font color="#%06x">%s</font></td>'%(color, inverted_color(color), '*'.join(strdata));
                        
                    fout.write('\n'.join([
                    '    <tr>%s<td>%s</td>'%(comb, '%s of %s'%(dcount, len(self.selected_datasets))),
                    '</tr>',
                    ]))
                
                fout.write('\n'.join([                
                '    </table>',
                ]));

              
            fout.write('\n'.join([                                
                '</body>',
                '</html>',
                ]));
        #Add filename and title for the overall list of reports        
        self.html_titles.append('Selected samples & Model groups');
        self.html_filenames.append('sample_model.html');
        
        
        
    def _generate_sample_selection_report(self):            
        #Table showing which samples and which retention times were selected for analysis
        printlog('\nGenerating sample selection report...');
        
        with open(os.path.join(self.output_prefix_with_path, 'samples.html'), 'w') as fout:
            fout.write('\n'.join([
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<title>Selected samples & rt times</title>',
                '</head>',
                '<body>',]));
                
            fout.write('\n'.join([
                '<h1>Selected samples & retention time peaks</h1>', 
                ]))                

            rt_string = [];
            cl = np.full((len(self.rts),), color_grey, np.int32); #Grey
            cl[self.rt_indeces] = color_green; #Green
            cl = cl.tolist();
            for i in range(len(self.rts)):
                rt_string.append('<th bgcolor="#%06x">%.3f min</th>'%(cl[i], self.rts[i] / 60.0));

            fout.write('\n'.join([
                '    <table border=1>',
                '    <tr><th>Sample</th>',
                ''.join(rt_string),
                '</tr>',
                ]));
            
            
            for i in range(len(self.all_dataset_names)):
                rt_string = [];
                row_data = self.quantity_integrals[self.all_indeces[i], :].tolist();
                if self.all_indeces[i] in self.sel_sets:
                    for j in range(len(self.rts)):
                        rt_string.append('<td bgcolor="#%06x">%.2f</td>'%(cl[j], row_data[j]));
                else:
                    for j in range(len(self.rts)):
                        rt_string.append('<td bgcolor="#%06x">%.2f</td>'%(color_grey, row_data[j]));
                    
                fout.write('     <tr><td>%s</td>'%self.all_dataset_names[i]);
                fout.write(''.join(rt_string));
                fout.write('</tr>\n');
                
                
            fout.write('\n'.join([                
                '    </table>',
                '</body>',
                '</html>',
                ]));
        #Add filename and title for the overall list of reports                
        self.html_titles.append('Selected samples & retention time peaks');
        self.html_filenames.append('samples.html');
        


    def _generate_group_selection_report(self):            
        #Show which groups of metadata were selected to be used in the stats. model
        printlog('\nGenerating sample group selection report...');
        
        with open(os.path.join(self.output_prefix_with_path, 'sample_meta.html'), 'w') as fout:
            fout.write('\n'.join([
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<title>Selected samples & MetaData groups</title>',
                '</head>',
                '<body>',]));
                
            fout.write('\n'.join([
                '<h1>Selected samples & MetaData groups</h1>', 
                ]))                

            
            all_meta = set();

            for i in range(len(self.all_dataset_names)):
                meta = mh5.get_metadata(self.h5file, self.h5readpath, self.all_dataset_names[i]);
                all_meta =  all_meta.union(set(meta.keys()));

            all_meta = list(all_meta);
            
            meta_string = [];
            
            sel_meta = set(self.unique_categories);

            vcolor = [];            
            
            for i in range(len(all_meta)):
                if all_meta[i] in sel_meta:
                    meta_string.append('<th bgcolor="#%06x">%s</th>'%(color_green, all_meta[i]));
                    vcolor.append(color_green);
                else:
                    meta_string.append('<th bgcolor="#%06x">%s</th>'%(color_grey, all_meta[i]));
                    vcolor.append(color_grey);
            
            fout.write('\n'.join([
                '    <table border=1>',
                '    <tr><th>Sample</th>',
                ''.join(meta_string),
                '</tr>',
                ]));
            
            
            for i in range(len(self.all_dataset_names)):
                meta_string = [];
                
                meta = mh5.get_metadata(self.h5file, self.h5readpath, self.all_dataset_names[i]);
                
                if self.all_indeces[i] in self.sel_sets:
                    for j in range(len(all_meta)):
                        if all_meta[j] in meta:
                            meta_string.append('<td bgcolor="#%06x">%s</td>'%(vcolor[j], meta[all_meta[j]]));
                        else:
                            meta_string.append('<td bgcolor="#%06x"></td>'%(color_grey));
                else:
                    for j in range(len(all_meta)):
                        if all_meta[j] in meta:
                            meta_string.append('<td bgcolor="#%06x">%s</td>'%(color_grey, meta[all_meta[j]]));
                        else:
                            meta_string.append('<td bgcolor="#%06x"></td>'%(color_grey));
                    
                fout.write('     <tr><td>%s</td>'%self.all_dataset_names[i]);
                fout.write(''.join(meta_string));
                fout.write('</tr>\n');
                
                
            fout.write('\n'.join([                
                '    </table>',
                '</body>',
                '</html>',
                ]));
        #Add filename and title for the overall list of reports                
        self.html_titles.append('Selected samples & Meta data');
        self.html_filenames.append('sample_meta.html');
        

    
    def _finalize_report(self):            
        #Generate the list of reports and the overall frame defining index HTML
        printlog('\nFinalising report...');
        
        with open(os.path.join(self.output_prefix_with_path, 'index.html'), 'w') as fout:
            fout.write('\n'.join([
                '<!DOCTYPE html>',
                '<html>',
                '<frameset cols="15%,85%">',
                '<frame src="report_tables.html">',
                '<frame src="%s" name="ReportTable">'%self.html_filenames[0],
                '</frameset>',
                '</html>',
                ]));

        tables = [];

        for i in range(len(self.html_titles)):
            tables.append('<tr><td><a href="%s" target="ReportTable">%s</a></td></tr>'%(self.html_filenames[i], self.html_titles[i]));

        with open(os.path.join(self.output_prefix_with_path, 'report_tables.html'), 'w') as fout:
            fout.write('\n'.join([
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<title>Tables</title>',
                '</head>',
                '<body>',
                '    <table border=0>',
                '    <tr><th>Report tables</th></tr>',
                '      ' + '\n      '.join(tables),
                '    </table>',
                '</body>',
                '</html>',
                ]));


    def _next_data_selection(self):
        #Fetch next data block for the analysis when the StatisticalModel.data is being iterated over
        self.current_index += 1;
        if self.current_index > len(self.rt_indeces) - 1:
            del self.meta_data_dictionary['quantity_integrals'];
            raise StopIteration();
        
        self.current_rt_index = self.rt_indeces[self.current_index];
        self.current_rt = self.rts[self.current_rt_index];
        
        data = self.quantity_integrals[:, self.current_rt_index];
        data = data[self.selected_dataset_indeces];
        
        self.meta_data_dictionary['quantity_integrals'] = data;

        return self.meta_data_dictionary;


    def data(self):
        #Start iteration by for data in self.data
        self.current_index = -1;
        return DataIterator(self);
   


    def initialize_output(self, parameters = {}, additional_groups = []):
        #Prepare the internal structures for results storage from statistical methods
        #parameters and additional_groups are provided by the selected statistical method class 
        #and can be method-specific
        printlog('\nInitializing output...');
        #Save selected statistical method parameters into HDF5 in 'setup' subgroup
        store_to_hdf5({'parameters':parameters, 'additional_groups':additional_groups}, self.h5file, self.h5writepath + '/setup', allow_overwrite = True);
        #Save the list of combinations used by the model
        store_to_hdf5(self.combinations, self.h5file, self.h5writepath + '/combinations', allow_overwrite = True);
        #register stat. method parameters
        self.output_parameters = parameters;
        self.additional_groups = additional_groups;
        #prepare a dictionary which tells the index of the combination based on its string representation
        self.combination_index = {};
        for i in range(len(self.model_clean)):
            self.combination_index[self.model_clean[i]] = i;
        #update the dictionary with additional groups generated by the stat. method selected    
        for i in range(len(self.additional_groups)):
            self.combination_index[self.additional_groups[i]] = i + len(self.model_clean);
        #create the self.model_clean_plus model list containing both model_clean and additional_groups    
        self.model_clean_plus = self.model_clean + self.additional_groups;    
        
        #Initialize dictionaries to hold result groups and their corresponding colors. 
        #result_groups will contain open 2D HDF5 datasets of size(N of selected rts, N of combinations + additional_groups)
        #and of type float64. The keys in this dictionary is the output parameter calculated by the stat. method
        #e.g.  result_groups['F'] will contain the calculated values for F factor for all combinations (incl. additional_groups)
        #and for all selected rts.
        #result_groups_color will contain 2D HDF5 datasets of the same sizes holding result associated colors as int64.
        #parameter_converter is the convenience dictionary which translates the original output name of the parameter to
        #the one used by this script stat model. E.g. parameter_converter['PR(>F)'] = 'p_value'
        self.result_groups = {};
        self.result_groups_color = {};
        self.parameter_converter = {};
        for i in self.output_parameters:
            parameter_group = self.output_parameters[i];
            for parameter in parameter_group:
                pname = parameter[0];
                porigname = parameter[2];
                self.parameter_converter[porigname] = pname;
                
                full_pname = self.h5writepath + '/' + pname;
                if full_pname in self.h5file:
                    self.result_groups[pname] = self.h5file[full_pname];
                    self.result_groups[pname].resize((len(self.selected_rts), len(self.combinations) + len(self.additional_groups)));
                else:
                    self.result_groups[pname] = self.h5file.create_dataset(full_pname, 
                                                                           shape = (len(self.selected_rts), len(self.combinations) + len(self.additional_groups)), 
                                                                           maxshape = (None, None), 
                                                                           chunks = True, 
                                                                           compression = "gzip", 
                                                                           compression_opts = 5, 
                                                                           dtype = np.float64);
                self.result_groups[pname][:, :] = -1.0;
                                                                               
                full_pname = self.h5writepath + '/' + pname + '_color';
                if full_pname in self.h5file:
                    self.result_groups_color[pname] = self.h5file[full_pname];
                    self.result_groups_color[pname].resize((len(self.selected_rts), len(self.combinations) + len(self.additional_groups)));
                else:
                    self.result_groups_color[pname] = self.h5file.create_dataset(full_pname, 
                                                                           shape = (len(self.selected_rts), len(self.combinations) + len(self.additional_groups)), 
                                                                           maxshape = (None, None), 
                                                                           chunks = True, 
                                                                           compression = "gzip", 
                                                                           compression_opts = 5, 
                                                                           dtype = np.int32);
                self.result_groups_color[pname][:, :] = 0xFFFFFF;
        
        #Save the list of selected rt values to HDF5
        result_rts_name = self.h5writepath + '/' + 'rts';
        if result_rts_name in self.h5file:
            result_rts = self.h5file[result_rts_name];
            result_rts.resize((len(self.selected_rts),));
        else:
            result_rts = self.h5file.create_dataset(result_rts_name,       
                                                    shape = (len(self.selected_rts),),
                                                    maxshape = (None, ), 
                                                    chunks = True, 
                                                    compression = "gzip", 
                                                    compression_opts = 5, 
                                                    dtype = np.float64);
                                                    
        result_rts[:] = self.selected_rts[:];
        #Save their indeces to HDF5
        result_rtindeces_name = self.h5writepath + '/' + 'rt_indeces';
        if result_rtindeces_name in self.h5file:
            result_rtindeces = self.h5file[result_rtindeces_name];
            result_rtindeces.resize((len(self.selected_rts),));
        else:
            result_rtindeces = self.h5file.create_dataset(result_rtindeces_name,       
                                                    shape = (len(self.selected_rts),),
                                                    maxshape = (None, ), 
                                                    chunks = True, 
                                                    compression = "gzip", 
                                                    compression_opts = 5, 
                                                    dtype = np.int64);
                                                    
        result_rtindeces[:] = self.rt_indeces[:];
        
        

  
    def store_results(self, results, results_color):
        printlog('\nStoring results...');
        #Parse and store the results sent by the stat. method
        for key in results:
            result_set = results[key];
            result_set_color = results_color[key];
            c_index = self.combination_index[key];
            for subkey in result_set:
                if subkey in self.parameter_converter:
                    pvalue = result_set[subkey];
                    pcolor = result_set_color[subkey];
                    pname = self.parameter_converter[subkey];
                    self.result_groups[pname][self.current_index, c_index] = pvalue;
                    self.result_groups_color[pname][self.current_index, c_index] = pcolor;
        
    def _generate_stat_report(self):
        #Generate overall report on statistical analysis results
        printlog('\nGenerating statistics report...');
        fname = '%s.html'%self._for_file_name(self.method_name);
        
        with open(os.path.join(self.output_prefix_with_path, fname), 'w') as fout:
            fout.write('\n'.join([
                '<!DOCTYPE html>',
                '<html>',
                '<head>',
                '<title>Results of %s analysis</title>'%self.method_name,
                '</head>',
                '<body>',
                '<h1>Results of %s analysis</h1>'%self.method_name, 
                '    <table border=1>',
                ]));                


            rt_inds = [];
            rt_mins = [];
            
            for i in range(len(self.grouping_indeces)):
                index = self.grouping_indeces[i];
                rt_inds.append(str(self.rt_indeces[index]));
                rt_mins.append('%.2f'%(self.selected_rts[index] / 60.0));

            
            rows = [];
            
            for key in sorted(self.output_parameters.keys()):
                rows.append('<th colspan=%s align="left">%s</th>'%(len(self.grouping_indeces) + 2, key));
                rows.append('<th rowspan="4">Measures</th><th rowspan="4">Groups</th><th colspan="%s" align="left">Retention time peak N</th>'%len(self.grouping_indeces));
                rows.append('<th>' + '</th><th>'.join(rt_inds) + '</th>');
                rows.append('<th colspan="%s" align="left">Retention time, min</th>'%len(self.grouping_indeces));
                rows.append('<th>' + '</th><th>'.join(rt_mins) + '</th>');
            
                parameters = self.output_parameters[key];
                for parameter in parameters:
                    pname = parameter[0];
                    indx = len(rows);
                    if len(self.combination_index) > 0:
                        for comb_key in sorted(self.combination_index.keys()):
                            row = [];
                            c_index = self.combination_index[comb_key];
                            for rti in range(len(self.grouping_indeces)):
                                index = self.grouping_indeces[rti];
                                value = self.result_groups[pname][index, c_index];
                                color = self.result_groups_color[pname][index, c_index];
                                if isnull(value):
                                    row.append('<td bgcolor="#%06x"><font color="#%06x">NaN</font></td>'%(color, inverted_color(color)));
                                else:    
                                    row.append('<td bgcolor="#%06x"><font color="#%06x">%.3f</font></td>'%(color, inverted_color(color), value));
                                
                            
                            rows.append(
                            '<th>%s</th>'%(self.model_clean_plus[self.combination_index[comb_key]]) +
                            ''.join(row));
                        rows[indx] = '<th rowspan="%s">%s</th>'%(len(self.combination_index), parameter[1]) + rows[indx];
                        
            fout.write('\n'.join([
                '<tr>',
                '</tr><tr>'.join(rows),
                '</tr>',
            ]));
            
            
            fout.write('\n'.join([                
                '    </table>',
                '</body>',
                '</html>',
                ]));
                
        self.html_titles.append('%s analysis results'%self.method_name);
        self.html_filenames.append(fname);

    @staticmethod
    def _for_file_name(name):
        #convert name into a string containing valid characters for the file name
        #unacceptable characters are replaced with '_'
        name = list(name);
        result = [];
        for i in range(len(name)):
            if name[i] in name_characters:
                result.append(name[i]);
            else:
                result.append('_');
        return ''.join(result);
    
    def _group_results(self):        
        printlog('\nGrouping results...');
        #Perform results grouping using KMeans
        #Make default grouping_indeces corresponding to the original sequence of selected rts
        self.grouping_indeces = np.arange(len(self.selected_rts), dtype = np.int64);
        try:
            #Prepare a list of results values according to which the grouping will be performed
            #Dictated by group_by parameter, weighted according to group_and_weights
            self.grouping_data = [];
            
            for rti in range(len(self.grouping_indeces)):
                group = [];
                for key in sorted(self.output_parameters.keys()):
                    parameters = self.output_parameters[key];
                    for parameter in parameters:
                        pname = parameter[0];
                        if pname in self.group_and_weights:
                            if len(self.combination_index) > 0:
                                for comb_key in sorted(self.combination_index.keys()):
                                    c_index = self.combination_index[comb_key];
                                    index = self.grouping_indeces[rti];
                                    value = self.result_groups[pname][index, c_index];
                                    if not isnull(value):
                                        group.append(value * self.group_and_weights[pname]);
                                    else:
                                        group.append(0.0);
                                    
                                        
                self.grouping_data.append(group);
            #convert to NumPy array for use by the KMeans method    
            self.grouping_data = np.array(self.grouping_data);
            
            
            #Calling KMeans from sklean
            kmeans = KMeans(n_clusters = self.n_groups).fit(self.grouping_data);
            
            #Get unique clusters from kmeans and counts of entries in those clusters        
            u, r, c = np.unique(kmeans.labels_, return_inverse = True, return_counts = True );
            print(u)
            print(r)
            print(c)
            z = np.argsort(-c); #Sort by counts biggest to smallest
            print(z)
            u_sorted = u[z];
            c_sorted = c[z];
            print(u_sorted)
            print(c_sorted)
            
            g_new = np.zeros((len(self.selected_rts),), dtype = np.int64); #initialize new grouping indeces
            cnt = 0;
            #Populate new grouping indeces according to clusters
            for i in range(len(u_sorted)):
                print(i)
                print(c_sorted[i], u_sorted[i])
                print(cnt, cnt + c_sorted[i])
                print(r == u_sorted[i])
                print(r)
                g_new[cnt:cnt + c_sorted[i]] = self.grouping_indeces[r == u_sorted[i]];
                cnt += c_sorted[i];
            #Assign new grouping indeces    
            self.grouping_indeces = g_new;                        
            
            
        except:
            printlog('Grouping failed')
            self.grouping_indeces = np.arange(len(self.selected_rts), dtype = np.int64);
            
            
        #Store grouping indeces into HDF5            
        grouping_name = self.h5writepath + '/' + 'grouping_indeces';
        if grouping_name in self.h5file:
            g_indeces = self.h5file[grouping_name];
            g_indeces.resize((len(self.selected_rts),));
        else:
            g_indeces = self.h5file.create_dataset(grouping_name,       
                                                        shape = (len(self.selected_rts),),
                                                        maxshape = (None, ), 
                                                        chunks = True, 
                                                        compression = "gzip", 
                                                        compression_opts = 5, 
                                                        dtype = np.int64);
        g_indeces[:] = self.grouping_indeces[:];
            
            
            
        #Store grouping parameters used
        store_to_hdf5({'groups':self.groups, 
                       'group_weights':self.group_weights,
                       }, 
                       self.h5file, self.h5writepath + '/grouping', allow_overwrite = True);
                                                            
        
  


class DataIterator: #Iterator class for StatisticalModel.data;
    def __init__(self, stat_model):
        self.stat_model = stat_model;

    def __iter__(self):
        return self;

    def next(self):#For compatability with Python 2 and 3
        return self.stat_model._next_data_selection();
    
    def __next__(self):#For compatability with Python 2 and 3
        return self.stat_model._next_data_selection();


        

        

if __name__ == "__main__": 
    #Testing section. Place tests here for this module
    print('Testing...')
    '''
    stat_model = StatisticalModel('(((C(dose)*C("drug")*C(\'time\'))))-(C(dose) - (C(test)-C(code)) + C(time):C(drug)) + C(drug)', 
                                  {'group_by':['variance'], 'group_weights':5.0, 'group_distance_function':'euclidean'} , None, 
                 0, 
                 0, 
                 0, 
                 0, 
                 0, 
                 0, 
                 0);
                 
    
'''    
