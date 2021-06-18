/*Copyright (c) 2013-2016, Rob Schmuecker
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* The name Rob Schmuecker may not be used to endorse or promote products
  derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL MICHAEL BOSTOCK BE LIABLE FOR ANY DIRECT,
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.*/

/* This modified version was created by Robin Schmid (https://github.com/robinschmid) for the global foodomics
 project (GFOP)
 */

// tree data internalized
// const treeData = [];

const root = PLACEHOLDER_JSON_DATA;

visitAll(root, node => node.originalChildren = node.children);

// turn off node dragging
const isNodeDragActive = false;

// char width - distance between categories
var charWidth = 6;
var lineHeight = 40;

// label font size
var labelSize = 12;

// base radius
var isScalingActive = true;
const maxRadius = 20;
var radius = 6;

// only show matched nodes by default
var isFilterMatched = true;

// colors
var lineColor = "#ccc";
var nodeStrokeColor = "steelblue";
var noChildrenColor = "white";
var hasChildrenColor = "#e8f4fa";
var bgColor = "gold";
var matchColor = "#095b85";
var pieColors = [matchColor, bgColor];

// Calculate total nodes, max label length
var totalNodes = 0;
var maxLabelLength = 0;
// variables for drag/drop
var selectedNode = null;
var draggingNode = null;
// panning variables
var panSpeed = 200;
var panBoundary = 20; // Within 20px from edges will pan when dragging.
// Misc. variables
var i = 0;
var duration = 750;

var zoomListener;
// size of the diagram
var viewerWidth;
var viewerHeight;
// tree builder
var tree;
// tooltip
var tooltipDiv;
// svg objects
var baseSvg;
var svgGroup;
// define a d3 diagonal projection for use by the node paths later on.
var diagonal = d3.svg.diagonal()
    .projection(function (d) {
        return [d.y, d.x];
    });
// for pie charts
var pie = d3.layout.pie()
    .sort(null)
    .value(function (d) {
        return d.occurrence_fraction;
    });

// functions to trigger from outside (html buttons)
function collapseAllAndUpdate() {
    if (root) {
        collapseToLevel(1)
        update(root);
        centerLeftNode(root);
    }
}

function expandMatchedAndUpdate() {
    if (root) {
        visitAll(root, expandAllMatches)
        update(root);
        centerLeftNode(root);
    }
}

function expandAllAndUpdate() {
    if (root) {
        visitAll(root, expand)
        update(root);
        centerLeftNode(root);
    }
}

function toggleScalingAndUpdate() {
    if (root) {
        isScalingActive = !isScalingActive;
        update(root);
    }
}

function toggleFilterMatched() {
    if (root) {
        isFilterMatched = !isFilterMatched;
        visitAll(root, filterMatched)

        update(root);
        centerLeftNode(root);
    }
}

// define the character width -> space between classes
d3.select("#inputCharWidth").on("input", function (d) {
    setCharWidth(this.value);
});
d3.select("#inputHeight").on("input", function (d) {
    setLineHeight(this.value);
});

// define font size
d3.select("#inputFontSize").on("input", function (d) {
    setLabelSize(this.value);
});

d3.select("#downloadSvg").on("click", function (d) {
    downloadSvg();
});

/**
 * Does not work at the moment
 *
 */
function downloadSvg() {
    var html = d3.select("svg")
        .attr("title", "svg_title")
        .attr("version", 1.1)
        .attr("xmlns", "http://www.w3.org/2000/svg")
        .node().parentNode.innerHTML;

    d3.select("#downloadSvg")
        .attr("href-lang", "image/svg+xml")
        .attr("href", "data:image/svg+xml;base64,\n" + btoa(unescape(encodeURIComponent(html))))
        .html("download", "tree.svg");
};


// initialize drop down style menu
var allGroup = ["default", "contrast", "B+W"]

// Initialize the button
var dropdownButton = d3.select("#styleCombo")
    .append('select')

// add the options to the button
dropdownButton // Add a button
    .selectAll('myOptions') // add all options
    .data(allGroup)
    .enter()
    .append('option')
    .text(function (d) {
        return d;
    }) // text showed in the menu
    .attr("value", function (d) {
        return d;
    }) // corresponding value returned by the button

// When the button is changed, update style
dropdownButton.on("change", function (d) {
    // recover the option that has been chosen
    var selectedOption = d3.select(this).property("value");

    if ("default" === selectedOption) {
        noChildrenColor = "white";
        hasChildrenColor = "#e8f4fa";
        bgColor = "gold";
        matchColor = "#095b85";
        lineColor = "#ccc";
        nodeStrokeColor = "steelblue";
    } else if ("contrast" === selectedOption) {
        noChildrenColor = "white";
        hasChildrenColor = "#e8f4fa";
        bgColor = "#E3BAFF";
        matchColor = "#118B8C";
        lineColor = "orange";
        nodeStrokeColor = "#8840F0";
    } else if ("B+W" === selectedOption) {
        noChildrenColor = "white";
        hasChildrenColor = "#f4f4f4";
        bgColor = "white";
        matchColor = "black";
        lineColor = "#ccc";
        nodeStrokeColor = "black";
    }

    pieColors = [matchColor, bgColor];
    update(root);
});

// size of the diagram
viewerWidth = $(document).width();
viewerHeight = $(document).height();

tree = d3.layout.tree()
    .size([viewerHeight, viewerWidth]);


// Call visit function to establish maxLabelLength
visitAll(root, function (d) {
    totalNodes++;
    maxLabelLength = Math.max(d.name.length, maxLabelLength);
});

// Sort the tree initially incase the JSON isn't in a sorted order.
sortTree();

// TODO: Pan function, can be better implemented.
function pan(domNode, direction) {
    var speed = panSpeed;
    if (panTimer) {
        clearTimeout(panTimer);
        translateCoords = d3.transform(svgGroup.attr("transform"));
        if (direction == 'left' || direction == 'right') {
            translateX = direction == 'left' ? translateCoords.translate[0] + speed : translateCoords.translate[0] - speed;
            translateY = translateCoords.translate[1];
        } else if (direction == 'up' || direction == 'down') {
            translateX = translateCoords.translate[0];
            translateY = direction == 'up' ? translateCoords.translate[1] + speed : translateCoords.translate[1] - speed;
        }
        scaleX = translateCoords.scale[0];
        scaleY = translateCoords.scale[1];
        scale = zoomListener.scale();
        svgGroup.transition().attr("transform", "translate(" + translateX + "," + translateY + ")scale(" + scale + ")");
        d3.select(domNode).select('g.node').attr("transform", "translate(" + translateX + "," + translateY + ")");
        zoomListener.scale(zoomListener.scale());
        zoomListener.translate([translateX, translateY]);
        panTimer = setTimeout(function () {
            pan(domNode, speed, direction);
        }, 50);
    }
}

// Define the zoom function for the zoomable tree
function zoom() {
    // var scale = Math.pow(d3.event.scale, .1);
    // var translateY = (viewerHeight - (viewerHeight * scale)) / 2;
    // var translateX = (viewerWidth - (viewerWidth * scale)) / 2;
    // svgGroup.attr("transform", "translate(" + [translateX, translateY] + ")" + " scale(" + scale + ")");

    svgGroup.attr("transform", "translate(" + d3.event.translate + ")scale(" + d3.event.scale + ")");
}

// define the zoomListener which calls the zoom function on the "zoom" event constrained within the scaleExtents
zoomListener = d3.behavior.zoom().scaleExtent([0.1, 3]).on("zoom", zoom);


function initiateDrag(d, domNode) {
    // skip dragging
    if (!isNodeDragActive) {
        return;
    }

    draggingNode = d;
    d3.select(domNode).select('.ghostCircle').attr('pointer-events', 'none');
    d3.selectAll('.ghostCircle').attr('class', 'ghostCircle show');
    d3.select(domNode).attr('class', 'node activeDrag');

    svgGroup.selectAll("g.node").sort(function (a, b) { // select the parent and sort the path's
        if (a.id != draggingNode.id) return 1; // a is not the hovered element, send "a" to the back
        else return -1; // a is the hovered element, bring "a" to the front
    });
    // if nodes has children, remove the links and nodes
    if (nodes.length > 1) {
        // remove link paths
        links = tree.links(nodes);
        nodePaths = svgGroup.selectAll("path.link")
            .data(links, function (d) {
                return d.target.id;
            }).remove();
        // remove child nodes
        nodesExit = svgGroup.selectAll("g.node")
            .data(nodes, function (d) {
                return d.id;
            }).filter(function (d, i) {
                if (d.id == draggingNode.id) {
                    return false;
                }
                return true;
            }).remove();
    }

    // remove parent link
    parentLink = tree.links(tree.nodes(draggingNode.parent));
    svgGroup.selectAll('path.link').filter(function (d, i) {
        if (d.target.id == draggingNode.id) {
            return true;
        }
        return false;
    }).remove();

    dragStarted = null;
}

// define the baseSvg, attaching a class for styling and the zoomListener
baseSvg = d3.select("#tree-container").append("svg")
    .attr("width", viewerWidth)
    .attr("height", viewerHeight)
    .attr("class", "overlay")
    .call(zoomListener);


// Define the drag listeners for drag/drop behaviour of nodes.
dragListener = d3.behavior.drag()
    .on("dragstart", function (d) {
        if (d == root) {
            return;
        }
        dragStarted = true;
        nodes = tree.nodes(d);
        d3.event.sourceEvent.stopPropagation();
        // it's important that we suppress the mouseover event on the node being dragged. Otherwise it will absorb the mouseover event and the underlying node will not detect it d3.select(this).attr('pointer-events', 'none');
    })
    .on("drag", function (d) {
        if (d == root) {
            return;
        }
        if (dragStarted) {
            domNode = this;
            initiateDrag(d, domNode);
        }

        // get coords of mouseEvent relative to svg container to allow for panning
        relCoords = d3.mouse($('svg').get(0));
        if (relCoords[0] < panBoundary) {
            panTimer = true;
            pan(this, 'left');
        } else if (relCoords[0] > ($('svg').width() - panBoundary)) {

            panTimer = true;
            pan(this, 'right');
        } else if (relCoords[1] < panBoundary) {
            panTimer = true;
            pan(this, 'up');
        } else if (relCoords[1] > ($('svg').height() - panBoundary)) {
            panTimer = true;
            pan(this, 'down');
        } else {
            try {
                clearTimeout(panTimer);
            } catch (e) {

            }
        }

        // drag node
        if (isNodeDragActive) {
            // shift node with mouse movement:
            d.x0 += d3.event.dy;
            d.y0 += d3.event.dx;
            var node = d3.select(this);
            node.attr("transform", "translate(" + d.y0 + "," + d.x0 + ")");
            updateTempConnector();
        }
    }).on("dragend", function (d) {
        // node dragging turned off
        if (!isNodeDragActive) {
            return;
        }

        if (d == root) {
            return;
        }
        domNode = this;
        if (selectedNode) {
            // now remove the element from the parent, and insert it into the new elements children
            var index = draggingNode.parent.children.indexOf(draggingNode);
            if (index > -1) {
                draggingNode.parent.children.splice(index, 1);
            }
            if (typeof selectedNode.children !== 'undefined' || typeof selectedNode._children !== 'undefined') {
                if (typeof selectedNode.children !== 'undefined') {
                    selectedNode.children.push(draggingNode);
                } else {
                    selectedNode._children.push(draggingNode);
                }
            } else {
                selectedNode.children = [];
                selectedNode.children.push(draggingNode);
            }
            // Make sure that the node being added to is expanded so user can see added node is correctly moved
            expand(selectedNode);
            sortTree();
            endDrag();
        } else {
            endDrag();
        }
    });

function endDrag() {
    selectedNode = null;
    d3.selectAll('.ghostCircle').attr('class', 'ghostCircle');
    d3.select(domNode).attr('class', 'node');
    // now restore the mouseover event or we won't be able to drag a 2nd time
    d3.select(domNode).select('.ghostCircle').attr('pointer-events', '');
    updateTempConnector();
    if (draggingNode !== null) {
        update(root);
        centerNode(draggingNode);
        draggingNode = null;
    }
}

var overCircle = function (d) {
    selectedNode = d;
    updateTempConnector();
};
var outCircle = function (d) {
    selectedNode = null;
    updateTempConnector();
};

// Function to update the temporary connector indicating dragging affiliation
var updateTempConnector = function () {
    var data = [];
    if (draggingNode !== null && selectedNode !== null) {
        // have to flip the source coordinates since we did this for the existing connectors on the original tree
        data = [{
            source: {
                x: selectedNode.y0,
                y: selectedNode.x0
            },
            target: {
                x: draggingNode.y0,
                y: draggingNode.x0
            }
        }];
    }
    var link = svgGroup.selectAll(".templink").data(data);

    link.enter().append("path")
        .attr("class", "templink")
        .attr("d", d3.svg.diagonal())
        .attr('pointer-events', 'none');

    link.attr("d", d3.svg.diagonal());

    link.exit().remove();
};

// add tooltip div and set to invisible for now
tooltipDiv = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

// Append a group which holds all nodes and which the zoom Listener can act upon.
svgGroup = baseSvg.append("g");

// Define the root
root.x0 = viewerHeight / 2;
root.y0 = 0;

// visitAll(root, expandAllMatches)
visitAll(root, filterMatched);
// Layout the tree initially and center left on the root node.
update(root);
centerLeftNode(root);

/**
 * Calculate radius for nodes and pie charts
 * @param matched_size
 * @returns {number}
 */
function calcRadius(matched_size) {
    return matched_size > 0 && isScalingActive ? Math.min(radius + Math.sqrt(matched_size), maxRadius) : radius;
}

// Toggle children on click.
function click(d) {
    if (d3.event.defaultPrevented) return; // click suppressed
    d = toggleChildren(d);
    update(d);
    centerNode(d);
}

function formatDecimals(value, decimals) {
    return Number(Math.round(value + 'e' + decimals) + 'e-' + decimals).toFixed(decimals);
}

function formatDecimals2(value, decimals) {
    return Number(value).toFixed(decimals);
}

// update view
function update(source) {
    // Compute the new height, function counts total children of root node and sets tree height accordingly.
    // This prevents the layout looking squashed when new nodes are made visible or looking sparse when nodes are removed
    // This makes the layout more consistent.
    var levelWidth = [1];
    var childCount = function (level, n) {
        if (n.children && n.children.length > 0) {
            if (levelWidth.length <= level + 1) levelWidth.push(0);

            levelWidth[level + 1] += n.children.length;
            n.children.forEach(function (d) {
                childCount(level + 1, d);
            });
        }
    };
    childCount(0, root);
    var newHeight = d3.max(levelWidth) * lineHeight; // 25 pixels per line
    tree = tree.size([newHeight, viewerWidth]);

    // Compute the new tree layout.
    var nodes = tree.nodes(root).reverse(),
        links = tree.links(nodes);

    // Set widths between levels based on maxLabelLength.
    nodes.forEach(function (d) {
        d.y = (d.depth * (maxLabelLength * charWidth)); //maxLabelLength * 10px
        // alternatively to keep a fixed scale one can set a fixed depth per level
        // Normalize for fixed-depth by commenting out below line
        // d.y = (d.depth * 500); //500px per level.
    });

    // Update the nodes…
    node = svgGroup.selectAll("g.node")
        .data(nodes, function (d) {
            return d.id || (d.id = ++i);
        });

    // Enter any new nodes at the parent's previous position.
    var nodeEnter = node.enter().append("g")
        .call(dragListener)
        .attr("class", "node")
        .attr("transform", function (d) {
            return "translate(" + source.y0 + "," + source.x0 + ")";
        })
        .on('click', click)
        .on("mouseover", function (d) {
            tooltipDiv.transition()
                .duration(200)
                .style("opacity", .9);
            tooltipDiv.html(
                // show mouse over tooltip. Just for the fun count the clicks in the click method
                "Name: " + d.name
                + (d.matched_size > 0 ? "<br/>Matches: " + d.matched_size : "")
                + (d.occurrence_fraction > 0 ? "<br/>Occurance fraction: " + formatDecimals(d.occurrence_fraction, 3) : "")
                + (d.group_size > 0 ? "<br/>Group size: " + d.group_size : "")
            )
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function (d) {
            tooltipDiv.transition()
                .duration(200)
                .style("opacity", 0);
        });

    nodeEnter.append("circle")
        .attr('class', 'nodeCircle')
        .attr("r", 0)
        .style("stroke", nodeStrokeColor)
        .style("fill", function (d) {
            return d._children ? hasChildrenColor : noChildrenColor;
        });


    // add pie chart
    nodeEnter.selectAll("g path")
        .data(function (d, i) {
            if (d.occurrence_fraction > 0) {
                return pie(d.pie_data);
            } else {
                return [];
            }
        })
        .enter()
        .append("svg:path")
        .attr('class', 'nodePie')
        .attr("fill", function (d, i) {
            return pieColors[d.data.index];
        })
        .attr("d", function (d) {
            return d3.svg.arc().outerRadius(calcRadius(d.data.matched_size))(d);
        });


    nodeEnter.append("text")
        .attr("x", function (d) {
            return d.children || d._children ? -10 : 10;
        })
        .attr("dy", ".35em")
        .attr('class', 'nodeText')
        .attr("text-anchor", function (d) {
            return d.children || d._children ? "end" : "start";
        })
        .text(function (d) {
            return d.name;
        })
        .style("fill-opacity", 0)
        .style("font-size", labelSize);

    // phantom node to give us mouseover in a radius around it
    nodeEnter.append("circle")
        .attr('class', 'ghostCircle')
        .attr("r", 30)
        .attr("opacity", 0.1) // change this to zero to hide the target area
        .style("fill", "red")
        .attr('pointer-events', 'mouseover')
        .on("mouseover", function (node) {
            overCircle(node);
        })
        .on("mouseout", function (node) {
            outCircle(node);
        });

    // Update the text to reflect whether node has children or not.
    node.select('text')
        .attr("x", function (d) {
            return d.children || d._children ? -10 : 10;
        })
        .attr("text-anchor", function (d) {
            return d.children || d._children ? "end" : "start";
        })
        .text(function (d) {
            return d.name;
        });

    // update pie charts
    // node.select("g path.nodePie")
    //     .attr("fill", function (d, i) {
    //         return pieColors[d.pie_data.index];
    //     })
    //     .attr("d", function (d) {
    //         return d3.svg.arc().outerRadius(calcRadius(d.data.matched_size))(d);
    //     });

    // Change the circle fill depending on whether it has children and is collapsed
    // node.select("circle.nodeCircle")
    //     .attr("r", function (d) {
    //         // set the radius if matches larger : otherwise default to X
    //         return d.matched_size > 0 ? Math.min(4.5 + Math.sqrt(d.matched_size), 20) : 4.5;
    //     })
    //     .style("fill", function (d) {
    //         // set fill color depending on matches and children
    //         var matches = d.matched_size
    //         if (matches > 0) {
    //             return d._children ? "goldenrod" : "gold";
    //         } else {
    //             return d._children ? "lightsteelblue" : "#fff";
    //         }
    //         return d._children ? "lightsteelblue" : "#fff";
    //     });
    node.select("circle.nodeCircle")
        .attr("r", function (d) {
            // set the radius if matches larger : otherwise default to X
            return calcRadius(d.matched_size);
        })
        .style("stroke", nodeStrokeColor)
        .style("fill", function (d) {
            // set fill color depending on matches and children
            var matches = d.matched_size
            if (matches > 0) {
                return matchColor;
            } else {
                return d._children ? hasChildrenColor : noChildrenColor;
            }
        })
    // .selectAll("path")
    // .data(function (d, i) {
    //     let occurrenceFraction = d.occurrence_fraction;
    //     return pie([occurrenceFraction, 1.0 - occurrenceFraction]);
    // })
    // .enter()
    // .append("svg:path")
    // .attr("d", arc)
    // .attr("fill", function (d, i) {
    //     return pieColors[i];
    // })
    ;

    // Transition nodes to their new position.
    var nodeUpdate = node.transition()
        .duration(duration)
        .attr("transform", function (d) {
            return "translate(" + d.y + "," + d.x + ")";
        });

    // Fade the text in
    nodeUpdate.select("text")
        .style("fill-opacity", 1)
        .style("font-size", labelSize);

    nodeUpdate.selectAll("path.nodePie")
        .attr("d", function (d) {
            return d3.svg.arc().outerRadius(calcRadius(d.data.matched_size))(d);
        })
        .attr("fill", function (d, i) {
            return pieColors[d.data.index];
        });

    // Transition exiting nodes to the parent's new position.
    var nodeExit = node.exit().transition()
        .duration(duration)
        .attr("transform", function (d) {
            return "translate(" + source.y + "," + source.x + ")";
        })
        .remove();

    nodeExit.select("circle")
        .attr("r", 0);

    nodeExit.select("text")
        .style("fill-opacity", 0)
        .style("font-size", labelSize);

    // Update the links…
    var link = svgGroup.selectAll("path.link")
        .data(links, function (d) {
            return d.target.id;
        });

    // Enter any new links at the parent's previous position.
    link.enter().insert("path", "g")
        .attr("class", "link")
        .style("stroke", lineColor)
        .attr("d", function (d) {
            var o = {
                x: source.x0,
                y: source.y0
            };
            return diagonal({
                source: o,
                target: o
            });
        });

    // Transition links to their new position.
    link.transition()
        .duration(duration)
        .style("stroke", lineColor)
        .attr("d", diagonal);

    // Transition exiting nodes to the parent's new position.
    link.exit().transition()
        .duration(duration)
        .attr("d", function (d) {
            var o = {
                x: source.x,
                y: source.y
            };
            return diagonal({
                source: o,
                target: o
            });
        })
        .remove();

    // Stash the old positions for transition.
    nodes.forEach(function (d) {
        d.x0 = d.x;
        d.y0 = d.y;
    });
}


function collapseAll() {
    visitAll(root, collapse);
}

// A recursive helper function for performing some setup by walking through all nodes

function visit(parent, visitFn, childrenFn) {
    if (!parent) return;

    visitFn(parent);

    var children = childrenFn(parent);
    if (children) {
        var count = children.length;
        for (var i = 0; i < count; i++) {
            visit(children[i], visitFn, childrenFn);
        }
    }
}

function visitAll(parent, visitFn) {
    visit(parent, visitFn, getAllChildren);
}

function visitAllToLevel(parent, level, visitFn, visitAfterLevelFn) {
    visitToLevel(parent, level, visitFn, visitAfterLevelFn, getAllChildren);
}

function visitToLevel(parent, level, visitFn, visitAfterLevelFn, childrenFn) {
    if (!parent) return;

    if (level > 0) {
        visitFn(parent);
    } else {
        visitAfterLevelFn(parent);
    }
    var children = childrenFn(parent);
    if (children) {
        var count = children.length;
        for (var i = 0; i < count; i++) {
            visitToLevel(children[i], (level - 1), visitFn, visitAfterLevelFn, childrenFn);
        }
    }
}

// get all children of parent
function getAllChildren(parent) {
    if (parent.children && parent.children.length > 0) {
        return parent.children;
    }
    if (parent._children && parent._children.length > 0) {
        return parent._children;
    }
    return null;
}

// sort the tree according to the node names
function sortTree() {
    tree.sort(function (a, b) {
        return b.name.toLowerCase() < a.name.toLowerCase() ? 1 : -1;
    });
}

// true if node has group_size>0 (matches)
function hasMatches(node) {
    return node.matched_size > 0;
}

// true if node has group_size>0 (matches)
function hasNoMatches(node) {
    return !hasMatches(node);
}

/**
 * Collapse the node and all it's children
 * @param node a node and its children
 * @param predicate a function to define if nodes should be collapsed (true) or shown (false). predicate should
 * take a node
 */
function expandAllMatches(node) {
    if (hasMatches(node)) {
        expand(node)
    } else {
        collapse(node)
    }
}


function collapseToLevel(level) {
    visitAllToLevel(root, level, expand, collapse);
}

// Helper functions for collapsing and expanding nodes.
function collapse(d) {
    if (d.children) {
        d._children = d.children;
        d._children.forEach(collapse);
        d.children = null;
        d.collapsed = true;
    }
}

function expand(d) {
    if (d._children) {
        d.children = d._children;
        d.children.forEach(expand);
        d._children = null;
        d.collapsed = false;
    }
}

function filterMatched(d) {
    if (typeof d.originalChildren !== 'undefined' && d.originalChildren.length > 0) {
        // set original children to children
        if (d.collapsed) d._children = d.originalChildren;
        else d.children = d.originalChildren;
        d.filteredChildren = null;
    }


    if (isFilterMatched) {
        if (d.children) {
            d.filteredChildren = d.children.filter(child => !(child.matched_size > 0));
            d.children = d.children.filter(child => child.matched_size > 0);
        }
        if (d._children) {
            d.filteredChildren = d._children.filter(child => !(child.matched_size > 0));
            d.children = d._children.filter(child => child.matched_size > 0);
        }
    }
}

// Function to center node when clicked/dropped so node doesn't get lost when collapsing/moving with large amount of children.
function centerNode(source) {
    scale = zoomListener.scale();
    x = -source.y0;
    y = -source.x0;
    x = x * scale + viewerWidth / 2;
    y = y * scale + viewerHeight / 2;
    d3.select('g').transition()
        .duration(duration)
        .attr("transform", "translate(" + x + "," + y + ")scale(" + scale + ")");
    zoomListener.scale(scale);
    zoomListener.translate([x, y]);
}

// Function to center node when clicked/dropped so node doesn't get lost when collapsing/moving with large amount of children.
function centerLeftNode(source) {
    scale = zoomListener.scale();
    x = -source.y0;
    y = -source.x0;
    x = x * scale + 40;
    y = y * scale + viewerHeight / 2;
    d3.select('g').transition()
        .duration(duration)
        .attr("transform", "translate(" + x + "," + y + ")scale(" + scale + ")");
    zoomListener.scale(scale);
    zoomListener.translate([x, y]);
}

// Toggle children function
function toggleChildren(d) {
    if (d.children) {
        d._children = d.children;
        d.children = null;
    } else if (d._children) {
        d.children = d._children;
        d._children = null;
    }
    return d;
}


function setLabelSize(value) {
    if (labelSize === value)
        return;
    else {
        console.log("Set label size to " + value);
        labelSize = value;
        update(root);
    }
}

function setCharWidth(value) {
    if (charWidth === value)
        return;
    else {
        console.log("Set label size to " + value);
        charWidth = value;
        update(root);
    }
}

function setLineHeight(value) {
    if (lineHeight === value)
        return;
    else {
        console.log("Set line height to " + value);
        lineHeight = value;
        update(root);
    }
}