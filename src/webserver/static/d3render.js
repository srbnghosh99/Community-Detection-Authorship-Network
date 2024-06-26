
//add the graph specified in d3data in the dom at the location specified by domid (parameter for d3select)
export function add_d3_graph(d3data, domid) {
    // set the dimensions and margins of the graph
    var margin = {top: 10, right: 30, bottom: 30, left: 40},
	width = 400 - margin.left - margin.right,
	height = 400 - margin.top - margin.bottom;

    var basedom = d3.select(domid)
    var infop = basedom.append("p");
    
    // append the svg object to the body of the page
    var svg = basedom
	.append("svg")
	.attr("width", width + margin.left + margin.right)
	.attr("height", height + margin.top + margin.bottom)
	.append("g")
	.attr("transform",
              "translate(" + margin.left + "," + margin.top + ")");
    

    // Initialize the links
    var link = svg
	.selectAll("line")
	.data(d3data.links)
	.enter()
	.append("line")
	.style("stroke", "#aaa")
    
    // Initialize the nodes
    var node = svg
	.selectAll("circle")
	.data(d3data.nodes)
	.enter()
	.append("circle")
	.attr("r", 20)
	.style("fill", "#69b3a2")
	.on('mouseover', function (event, d) {
	    console.log("hover");
	    infop.text("vertexid: "+d.id);
	});
    
    // Let's list the force we wanna apply on the network
    var simulation = d3.forceSimulation(d3data.nodes)                 // Force algorithm is applied to d3data.nodes
	.force("link", d3.forceLink()                               // This force provides links between nodes
	       .id(function(d) { return d.id; })                     // This provide  the id of a node
	       .links(d3data.links)                                    // and this the list of links
	      )
	.force("charge", d3.forceManyBody().strength(-400))         // This adds repulsion between nodes. Play with the -400 for the repulsion strength
	.force("center", d3.forceCenter(width / 2, height / 2))     // This force attracts nodes to the center of the svg area
	.on("end", ticked);
    
    // This function is run at each iteration of the force algorithm, updating the nodes position.
    function ticked() {
	link
	    .attr("x1", function(d) { return d.source.x; })
	    .attr("y1", function(d) { return d.source.y; })
	    .attr("x2", function(d) { return d.target.x; })
	    .attr("y2", function(d) { return d.target.y; });
	
	node
	    .attr("cx", function (d) { return d.x; })
	    .attr("cy", function(d) { return d.y; });
    }
}
