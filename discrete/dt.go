package main

// AddNode is a node in ADD
type AddNode struct {
	id         int
	hi         int
	lo         int
	pweight    float64
	nweight    float64
	isDecision bool
	isITE      bool
	isAdd      bool
}

//ADD represents an ADD instance
type ADD struct {
	addNodes []AddNode
	root     int
}

/*TODO: think of an ADD solution structure */

//ADDSolution represents a solution to an ADD instance
type ADDSolution struct {
	decisionVariables map[int]bool
	value             float64
}

func makeZeroTerminal() ADD {
	terminalNode := AddNode{id: -1, hi: 0, lo: 0, pweight: 0.0, nweight: 0.0, isDecision: false}
	nodes := make([]AddNode, 1, 1)
	nodes[0] = terminalNode
	add := ADD{addNodes: nodes, root: 0}
	return add
}

func makeOneTerminal() ADD {
	terminalNode := AddNode{id: -2, hi: 0, lo: 0, pweight: 0.0, nweight: 0.0, isDecision: false}
	nodes := make([]AddNode, 1, 1)
	nodes[0] = terminalNode
	add := ADD{addNodes: nodes, root: 0}
	return add
}

func emptyADD() ADD {
	var empty ADD
	return empty
}

func multiplyADD(add ADD, constant float64) ADD {
	/*TODO: think of a way to make a ADD after multiplying a constant number */
	return ADD{addNodes: make([]AddNode, 0, 0), root: 0}
}
func findMaxID(addNodes []AddNode) int {
	/*TODO: id of the node should be the max id of the other nodes+1 */
	maxID := 0
	for i := 0; i < len(addNodes); i++ {
		if addNodes[i].id > maxID {
			maxID = addNodes[i].id
		}
	}
	return maxID
}

func addADD(add1 ADD, add2 ADD) ADD {
	allNodes := append(add1.addNodes, add2.addNodes...)
	nodeID := findMaxID(allNodes)
	node := AddNode{id: nodeID, hi: add1.root, lo: add2.root, pweight: 1.0, nweight: 1.0, isDecision: false, isITE: false, isAdd: true}
	allNodes = append(allNodes, node)
	return ADD{addNodes: allNodes, root: node.id}
}

func iteADD(node BddNode, loAdd ADD, hiAdd ADD) ADD {
	allNodes := append(loAdd.addNodes, hiAdd.addNodes...)
	nodeID := findMaxID(allNodes)
	iteNode := AddNode{id: nodeID, hi: hiAdd.root, lo: loAdd.root, pweight: 1.0, nweight: 1.0, isDecision: false, isITE: true, isAdd: false}
	allNodes = append(allNodes, iteNode)
	return ADD{addNodes: allNodes, root: node.id}
}

func probabilityDD(bdd BDD, solution map[int]bool, nodeID int) ADD {
	if nodeID == -1 {
		return makeZeroTerminal()
	}
	if nodeID == -2 {
		return makeOneTerminal()
	}

	node := bdd.bddNodes[nodeID]
	variable := bdd.bddVars[node.varid]
	var nodeValue ADD
	hiADD := multiplyADD(probabilityDD(bdd, solution, node.hi), variable.pweight)
	loADD := multiplyADD(probabilityDD(bdd, solution, node.lo), variable.nweight)
	if !variable.isDecision {
		nodeValue = addADD(hiADD, loADD)
	} else {
		nodeValue = iteADD(node, hiADD, loADD)
	}

	return nodeValue
}

func getExactADDSolution(add ADD) ADDSolution {
	/* Max ADD soultion given deciison variables */
	var emptySolution map[int]bool
	return ADDSolution{decisionVariables: emptySolution, value: 0.0}
}

func getApproximateADDSolution(bdd BDD) ADDSolution {
	/* Max ADD soultion given deciison variables */
	var emptySolution map[int]bool
	return ADDSolution{decisionVariables: emptySolution, value: 0.0}
}
