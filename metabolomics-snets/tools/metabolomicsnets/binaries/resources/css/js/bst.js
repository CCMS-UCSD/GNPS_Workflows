/*
 * File: bst.js
 *
 * A pure JavaScript implementation of a binary search tree.
 *
 */

/*
 * Class: BST
 *
 * The binary search tree class.
 *
 */
var BST = function () {
        /*
        * Private Class: Node
        *
        * A BST node constructor
        *
        * Parameters:
        *        leftChild - a reference to the left child of the node.
        *        key - The key of the node.
        *        value - the value of the node.
        *        rightChild - a reference to the right child of the node.
        *        parent - a reference to the parent of the node.
        *
        * Note: All parameters default to null.
        */
    var Node = function (leftChild, key, value, rightChild, parent) {
            return {
                leftChild: (typeof leftChild === "undefined") ? null : 
                           leftChild,
                key: (typeof key === "undefined") ? null : key,
                value: (typeof value === "undefined") ? null : value,
                rightChild: (typeof rightChild === "undefined") ? null : 
                            rightChild,
                parent: (typeof parent === "undefined") ? null : parent
            };
        },
        
        /*
         * Private Variable: root
         *
         * The root nade of the BST.
         */
        root = new Node(),
        
        /*
         * Private Method: searchNode
         *
         * Search through a binary tree.
         *
         * Parameters:
         *     node - the node to search on.
         *     key - the key to search for (as an integer).
         *
         * Returns:
         *     the value of the found node,
         *     or null if no node was found.
         *
         */
        searchNode = function (node, key) {
            if (node.key === null) {
                return null; // key not found
            }
            
            var nodeKey = parseInt(node.key, 10);

            if (key < nodeKey) {
                return searchNode(node.leftChild, key);
            } else if (key > nodeKey) {
                return searchNode(node.rightChild, key);
            } else { // key is equal to node key
                //return node.value;
                return node;
            }
        },
        
        /*
         * Private Method: insertNode
         *
         * Insert into a binary tree.
         *
         * Parameters:
         *     node - the node to search on.
         *     key - the key to insert (as an integer).
         *     value - the value to associate with the key (any type of 
         *             object).
         *
         * Returns:
         *     true.
         *
         */
        insertNode = function (node, key, value, parent) {
            if (node.key === null) {
                node.leftChild = new Node();
                node.key = key;
                node.value = value;
                node.rightChild = new Node();
                node.parent = parent;
                return true;
            }
            
            var nodeKey = parseInt(node.key, 10);

            if (key < nodeKey) {
                insertNode(node.leftChild, key, value, node);
            } else if (key > nodeKey) {
                insertNode(node.rightChild, key, value, node);
            } else { // key is equal to node key, update the value
                node.value = value;
                return true;
            }
        },
    
        /*
         * Private Method: traverseNode
         *
         * Call a function on each node of a binary tree.
         *
         * Parameters:
         *     node - the node to traverse.
         *     callback - the function to call on each node, this function 
         *                takes a key and a value as parameters.
         *
         * Returns:
         *     true.
         *
         */
        traverseNode = function (node, callback) {
            if (node.key !== null) {
                traverseNode(node.leftChild, callback);
                callback(node.key, node.value);
                traverseNode(node.rightChild, callback);
            }
            
            return true;
        },
        
        /*
         * Private Method: minNode
         *
         * Find the key of the node with the lowest key number.
         *
         * Parameters:
         *     node - the node to traverse.
         *
         * Returns: the key of the node with the lowest key number.
         *
         */
        minNode = function (node) {
            while (node.leftChild.key !== null) {
                node = node.leftChild;
            }

            return node.key;
        },

        /*
         * Private Method: maxNode
         *
         * Find the key of the node with the highest key number.
         *
         * Parameters:
         *     node - the node to traverse.
         *
         * Returns: the key of the node with the highest key number.
         *
         */
        maxNode = function (node) {
            while (node.rightChild.key !== null) {
                node = node.rightChild;
            }

            return node.key;
        },
        
        /*
         * Private Method: successorNode
         *
         * Find the key that successes the given node.
         *
         * Parameters:
		 *		node - the node to find the successor for
         *
         * Returns: the key of the node that successes the given node.
         *
         */
        successorNode = function (node) {
            var parent;
        
            if (node.rightChild.key !== null) {
                return minNode(node.rightChild);
            }
            
            parent = node.parent;
            while (parent.key !== null && node == parent.rightChild) {
                node = parent;
                parent = parent.parent;
            }
            
            return parent.key;
        },

        /*
         * Private Method: predecessorNode
         *
         * Find the key that preceeds the given node.
         *
         * Parameters:
		 *		node - the node to find the predecessor for
         *
         * Returns: the key of the node that preceeds the given node.
         *
         */
        predecessorNode = function (node) {
            var parent;
        
            if (node.leftChild.key !== null) {
                return maxNode(node.leftChild);
            }
            
            parent = node.parent;
            while (parent.key !== null && node == parent.leftChild) {
                node = parent;
                parent = parent.parent;
            }
            
            return parent.key;
        };
        
    return {
        /*
         * Method: search
         *
         * Search through a binary tree.
         *
         * Parameters:
         *     key - the key to search for.
         *
         * Returns:
         *     the value of the found node,
         *     or null if no node was found,
         *     or undefined if no key was specified.
         *
         */
        search: function (key) {
            var keyInt = parseInt(key, 10);

            if (isNaN(keyInt)) {
                return undefined; // key must be a number
            } else {
                return searchNode(root, keyInt);
            }
        },

        /*
         * Method: insert
         *
         * Insert into a binary tree.
         *
         * Parameters:
         *     key - the key to search for.
         *     value - the value to associate with the key (any type of 
         *             object).
         *
         * Returns:
         *     true,
         *     or undefined if no key was specified.
         *
         */
        insert: function (key, value) {
            var keyInt = parseInt(key, 10);
            
            if (isNaN(keyInt)) {
                return undefined; // key must be a number
            } else {
                return insertNode(root, keyInt, value, null);
            }
        },
        
        /*
         * Method: traverse
         *
         * Call a function on each node of a binary tree.
         *
         * Parameters:
         *     callback - the function to call on each node, this function 
         *                takes a key and a value as parameters. If no 
         *                callback is specified, print is called.
         *
         * Returns:
         *     true.
         *
         */
        traverse: function (callback) {
            if (typeof callback === "undefined") {
                callback = function (key, value) {
                    print(key + ": " + value);
                };
            }

            return traverseNode(root, callback);
        },

        /*
         * Method: min
         *
         * Find the key of the node with the lowest key number.
         *
         * Parameters: none
         *
         * Returns: the key of the node with the lowest key number.
         *
         */
        min: function () {
            return minNode(root);
        },

        /*
         * Method: max
         *
         * Find the key of the node with the highest key number.
         *
         * Parameters: none
         *
         * Returns: the key of the node with the highest key number.
         *
         */
        max: function () {
            return maxNode(root);
        },
		
        /*
         * Method: successor
         *
         * Find the key that successes the root node.
         *
         * Parameters: none
         *
         * Returns: the key of the node that successes the root node.
         *
         */
		successor: function () {
			return successorNode(root);
		},

        /*
         * Method: predecessor
         *
         * Find the key that preceeds the root node.
         *
         * Parameters: none
         *
         * Returns: the key of the node that preceeds the root node.
         *
         */
		predecessor: function () {
			return predecessorNode(root);
		}
	};
};

/*
 * Tests
 */

//var ipTree = new BST();
//ipTree.insert(4, "test4");
//ipTree.insert(1, "test1");
//ipTree.insert(10, "test10");
//ipTree.insert(2, "test2");
//ipTree.insert(3, "test3");
//ipTree.insert(9, "test9");
//ipTree.insert(8, "test8");
//ipTree.insert(5, "test5");
//ipTree.insert(7, "test7");
//ipTree.insert(6, "test6");

//ipTree.traverse(function (key, value) {
//    alert("The value of " + key + " is " + value + ".");
//});

//alert("Searching for 3 results in: " + ipTree.search(3));

//alert("Min is " + ipTree.min());
//alert("Max is " + ipTree.max());

//alert("The successor of root is: " + ipTree.successor());
//alert("The predecessor of root is: " + ipTree.predecessor());

/*
 * License:
 *
 * Copyright (c) 2011 Trevor Lalish-Menagh (http://www.trevmex.com/)
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 * 
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 * 
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */