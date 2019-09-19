////////////////////////////////////////////////////////////////////////////////
// spsReportSingle dynamic pagination and sorting for static reports
//
// By jcanhita@eng.ucsd.edu on aug/2012
//
////////////////////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////////////

// number of elements per page
var PAGE_LENGTH = 10;

var stIsIE = /*@cc_on!@*/false;

////////////////////////////////////////////////////////////////////////////////
// Message to be displayed on connection error.

////////////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////////////

// table control array
var TC = [];

////////////////////////////////////////////////////////////////////////////////
// Images
////////////////////////////////////////////////////////////////////////////////

var workingImage = "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";


////////////////////////////////////////////////////////////////////////////////
// Initializers
////////////////////////////////////////////////////////////////////////////////

// Initialize page variables from HTML initial page
function init(tabData, tabDataHeader)
{
  for(var i = 0 ; i < tabData.length ; i++) {
    // prepare for ith table
    TC[i] = [];
    // index 0: current start index
    TC[i][0] = 0;
    // index 1: current page length
    TC[i][1] = PAGE_LENGTH;
    // index 2: Current sort column
    TC[i][2] = -1;
    // index 3: ID column (for pagination)
    TC[i][3] = 0;
    // index 4: Current sort direction
    TC[i][4] = 0;
  }

  buildTables(tabData, tabDataHeader);
}
////////////////////////////////////////////////////////////////////////////////
function buildTablePaginationBar(tab, tabData)
{
  var aux = [];

  col  = TC[tab][3];
  curr = TC[tab][0];
  len  = TC[tab][1];

  if(tabData.length <= len)
    return aux;


  //for(var i = 0 ; i < tabData.length ; i++) {
  //  aux[i] = tabData[i][col];
  //}

  //aux.sort();
  var j = 0;

  for(var i = 0 ; i < tabData.length ; i += len ) {

    var first  = tabData[i][col];
    var b      = Math.min(tabData.length-1, i + len -1);
    var second = tabData[b][col];

    var str = '[' + first + '&nbsp;-&nbsp;' + second + ']';
    if(first == second)
      str = '[' + first  + ']';
    var stripped = str.replace(/(<([^>]+)>)/ig,"");

    aux[j++] =  stripped;
  }

  var ret = "<br><center>";

  for(var i = 0 ; i < aux.length ; i++) {
    if(i == curr / len)
      ret += "<span style='color: #ff0000;'>" + aux[i] + "</span> ";
    else
      ret += "<a href='#' onclick='TC[" + tab + "][0]=" + i * len + ";buildTable(" + tab + ",D, DH);'>" + aux[i] + "</a> ";
  }

  ret += "<center><br>";

  return ret;
}
////////////////////////////////////////////////////////////////////////////////
function buildTable(tab, tabData, tabDataHeader)
{
  // get needed elements
  var tabID = "tab_" + tab;
  var target1 = document.getElementById(tabID);
  if(target1)
    target1.innerHTML = "<table align='center'><tr><td align='center'><img src='data:image/gif;base64," + workingImage + "' /></td></tr></table>";

  var tabID = "bar_top_" + tab;
  var target2 = document.getElementById(tabID);
  if(target2)
    target2.innerHTML = "";

  var tabID = "bar_bot_" + tab;
  var target3 = document.getElementById(tabID);
  if(target3)
    target3.innerHTML = "";

  // create reference for storing return data
  var out = createReference("");
  // build pagination bar
  var bar = buildTablePaginationBar(tab, tabData[tab]);
  // build the table header
  buildTableHeader(out, tabDataHeader[tab], tab);
  // build the table body
  buildTableBody(out, tabData[tab], TC[tab][0], TC[tab][1]);

  // set the data
  if(target1)
    target1.innerHTML = out;
  if(target2)
    target2.innerHTML = bar;
  if(target3)
    target3.innerHTML = bar;
}
////////////////////////////////////////////////////////////////////////////////
function buildTables(tabData, tabDataHeader)
{
  // create reference for storing return data
  var out = createReference("");

  for(tab = 0 ; tab < tabData.length ; tab++) {
    buildTable(tab, tabData, tabDataHeader);
  }
}
////////////////////////////////////////////////////////////////////////////////
function buildTableHeader(out, tabDataHeader, tab)
{
  addToReference(out, "<thead>");
  for(row = 0 ; row < tabDataHeader.length ; row++) {
    addToReference(out, "<tr>");
    for(cel = 0 ; cel < tabDataHeader[row].length ; cel++) {
      addToReference(out, "<th onclick='sortColumn(" + tab + "," + cel + ");'><span style='color:white'>");
      aux = tabDataHeader[row][cel];
      if(TC[tab][2] == cel)
        if(TC[tab][4] == 2)
          aux += (stIsIE ? "&nbsp<font face='webdings'>6</font>" : "&nbsp;&#x25BE;");
        else
          aux += (stIsIE ? "&nbsp<font face='webdings'>5</font>" : "&nbsp;&#x25B4;");
      addToReference(out, aux);
      addToReference(out, "</span></th>");
    }
    addToReference(out, "</tr>");
  }
  addToReference(out, "</thead>");
}////////////////////////////////////////////////////////////////////////////////
function buildTableBody(out, tabData, start, size)
{
  addToReference(out, "<tbody>");
  for(row = start ; row < start + size && row < tabData.length ; row++) {
    addToReference(out, "<tr align='center' valign='middle'>");
    for(cel = 0 ; cel < tabData[row].length ; cel++) {
      addToReference(out, "<td align='center' valign='middle'>");
      addToReference(out, tabData[row][cel]);
      addToReference(out, "</td>");
    }
    addToReference(out, "</tr>");
  }
  addToReference(out, "</tbody>");
}
////////////////////////////////////////////////////////////////////////////////
// Table sorting
////////////////////////////////////////////////////////////////////////////////
function propComparator(col, dir) {
  return function(a, b) {
    aa = a[col].replace(/(<([^>]+)>)/ig,"");
    bb = b[col].replace(/(<([^>]+)>)/ig,"");
    if (aa.match(/^-?[£$¤]?[\d,.]+%?$/) && bb.match(/^-?[£$¤]?[\d,.]+%?$/)) {
      aa = parseFloat(aa.replace(/[^0-9.-]/g,''));
      if (isNaN(aa)) aa = 0;
      bb = parseFloat(bb.replace(/[^0-9.-]/g,''));
      if (isNaN(bb)) bb = 0;
      if(dir == 2)
        return bb-aa;
      return aa-bb;
    }

    if (aa == bb) return 0;
    if (aa < bb && dir == 2) return 1;
    if (aa < bb) return -1;
    if(dir == 2) return -1;
    return 1;
    //return a[col] - b[col];
  }
}
////////////////////////////////////////////////////////////////////////////////
function reverseTable(tab)
{
  var j = tab.length / 2;
  for(var i = 0 ; i < j ; i++) {
    var aux = tab[i];
    tab[i] = tab[tab.length - i - 1];
    tab[tab.length - i - 1] = aux;
  }
}
////////////////////////////////////////////////////////////////////////////////
function sortColumn(tab, col)
{
  // check if sort column is the same. If so, swich directionl.
  if(TC[tab][2] == col) {
    if(TC[tab][4] == 1)
      TC[tab][4] = 2;
    else
      TC[tab][4] = 1;
    reverseTable(D[tab]);
  } else {
    // set the current col
    TC[tab][2] = col;
    // direction is increasing
    TC[tab][4] = 1;

    // change pagination legends
    //TC[tab][3] = col;
    D[tab].sort(propComparator(col, TC[tab][4]));
    //shaker_sort(D[tab], propComparator(col, TC[tab][4]) );
  }

  buildTable(tab, D, DH);
}
////////////////////////////////////////////////////////////////////////////////
function shaker_sort(list, comp_func)
{
  // A stable sort function to allow multi-level sorting of data
  // see: http://en.wikipedia.org/wiki/Cocktail_sort
  var b = 0;
  var t = list.length - 1;
  var swap = true;

  while(swap) {
    swap = false;
    for(var i = b; i < t; ++i) {
      if ( comp_func(list[i], list[i+1]) > 0 ) {
        var q = list[i]; list[i] = list[i+1]; list[i+1] = q;
        swap = true;
      }
    } // for
    t--;

    if (!swap) break;

    for(var i = t; i > b; --i) {
      if ( comp_func(list[i], list[i-1]) < 0 ) {
        var q = list[i]; list[i] = list[i-1]; list[i-1] = q;
        swap = true;
      }
    } // for
    b++;

  } // while(swap)
}
////////////////////////////////////////////////////////////////////////////////
;(function() {
 
  var defaultComparator = function (a, b) {
    if (a < b) {
      return -1;
    }
    if (a > b) {
      return 1;
    }
    return 0;
  }
 
  Array.prototype.mergeSort = function( comparator ) {
    var i, j, k,
        firstHalf,
        secondHalf,
        arr1,
        arr2;
 
    if (typeof comparator != "function") { comparator = defaultComparator; }
 
    if (this.length > 1) {
      firstHalf = Math.floor(this.length / 2);
      secondHalf = this.length - firstHalf;
      arr1 = [];
      arr2 = [];
 
      for (i = 0; i < firstHalf; i++) {
        arr1[i] = this[i];
      }
 
      for(i = firstHalf; i < firstHalf + secondHalf; i++) {
        arr2[i - firstHalf] = this[i];
      }
 
      arr1.mergeSort( comparator );
      arr2.mergeSort( comparator );
 
      i=j=k=0;
 
      while(arr1.length != j && arr2.length != k) {
        if ( comparator( arr1[j], arr2[k] ) <= 0 ) {
          this[i] = arr1[j];
          i++;
          j++;
        } 
        else {
          this[i] = arr2[k];
          i++;
          k++;
        }
      }
 
      while (arr1.length != j) {
        this[i] = arr1[j];
        i++;
        j++;
      }
 
      while (arr2.length != k) {
        this[i] = arr2[k];
        i++;
        k++;
      }
    }
  }
})();
////////////////////////////////////////////////////////////////////////////////
// Reference Utilities
////////////////////////////////////////////////////////////////////////////////
// Create a variable reference to allow primitive data types to be passed-by-reference
function createReference(value)
{
   var newVar = new Array();
   newVar[0] = value;
   return newVar;
}
////////////////////////////////////////////////////////////////////////////////
// set reference variable's value
function setReference(val, value)
{
   val[0] = value;
}
////////////////////////////////////////////////////////////////////////////////
// add to variable
function addToReference(val, value)
{
   val[0] += value;
}
////////////////////////////////////////////////////////////////////////////////
