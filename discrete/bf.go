package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

// BddNode is a node in BDD
type BddNode struct {
	id    int
	varid int
	hi    int
	lo    int
}

//BddVar is a variable which corresponds to some BddNode
type BddVar struct {
	id         int
	pweight    float64
	nweight    float64
	isDecision bool
}

//BDD represents an BDD instance
type BDD struct {
	bddNodes []BddNode
	bddVars  []BddVar
	roots    map[int]bool
	maxVars  []int
}

func readBdd(bddFileName string) BDD {
	bytes, _ := ioutil.ReadFile(bddFileName)
	lines := strings.Split(string(bytes), "\n")

	l1 := strings.Split(lines[0], " ")
	numberOfNodes, _ := strconv.Atoi(l1[0])
	numberOfVariables, _ := strconv.Atoi(l1[1])

	l2 := strings.Split(lines[1], " ")
	roots := make(map[int]bool)
	for i := 0; i < len(l2); i++ {
		r, _ := strconv.Atoi(l2[i])
		roots[r] = true
	}

	bddNodes := make([]BddNode, numberOfNodes)

	for i := 0; i < numberOfNodes; i++ {
		nodeInfo := strings.Split(lines[i+2], " ")
		variable, _ := strconv.Atoi(nodeInfo[0])
		lo, _ := strconv.Atoi(nodeInfo[1])
		hi, _ := strconv.Atoi(nodeInfo[2])
		bddNodes[i] = BddNode{i, variable, hi, lo}
	}

	bddVars := make([]BddVar, numberOfVariables)

	weightStrs := strings.Split(lines[numberOfNodes+2], " ")
	for i := 0; i < numberOfVariables; i++ {
		bddVars[i].id = i
		bddVars[i].isDecision = false
		bddVars[i].pweight, _ = strconv.ParseFloat(weightStrs[i*2], 32)
		bddVars[i].nweight, _ = strconv.ParseFloat(weightStrs[i*2+1], 32)
	}

	maxVarStr := strings.Split(lines[numberOfNodes+3], " ")
	numMaxVars := len(maxVarStr)
	maxVars := make([]int, numMaxVars)
	for i := 0; i < numMaxVars; i++ {
		maxVar, _ := strconv.Atoi(maxVarStr[i])
		maxVars[i] = maxVar
		bddVars[maxVar].isDecision = true
	}

	return BDD{bddNodes, bddVars, roots, maxVars}
}

func childStr(child int) string {
	var target string
	switch child {
	case -2:
		target = "ntrue"
	case -1:
		target = "nfalse"
	default:
		target = fmt.Sprintf("n%d", child)
	}
	return target
}

func drawBdd(bdd BDD, filename string) {
	dotStr := "digraph G {\n\tntrue [shape=box,label=\"1\"];\n\tnfalse [shape=box,label=\"0\"];\n"
	for _, node := range bdd.bddNodes {
		description := fmt.Sprintf("label=\"v%d (%d)\"", node.varid, node.id)
		if bdd.bddVars[node.varid].isDecision {
			description += ",shape=diamond"
		}
		dotStr += fmt.Sprintf("\tn%d [%s];\n", node.id, description)
	}

	for _, node := range bdd.bddNodes {
		var target string
		bddVar := bdd.bddVars[node.varid]

		var properties = ""
		if !bddVar.isDecision {
			properties = fmt.Sprintf(" [label=\"%.2f\"]", bddVar.pweight)
		}
		target = childStr(node.hi)
		dotStr += fmt.Sprintf("\tn%d -> %s%s;\n", node.id, target, properties)

		properties = ""
		if !bddVar.isDecision {
			properties = fmt.Sprintf(",label=\"%.2f\"", bddVar.nweight)
		}
		target = childStr(node.lo)
		dotStr += fmt.Sprintf("\tn%d -> %s [style=dashed%s];\n", node.id, target, properties)
	}
	dotStr += "}\n"
	tempfile, _ := ioutil.TempFile("", "")
	tempfile.WriteString(dotStr)
	cmd := exec.Command("dot", "-Tpdf", tempfile.Name(),
		"-o", filename)
	cmd.Run()
	os.Remove(tempfile.Name())
}

func getValue(bdd BDD, solution map[int]bool, values []float64, nodeID int) float64 {
	if nodeID == -1 {
		return 0.0
	}
	if nodeID == -2 {
		return 1.0
	}
	if values[nodeID] != -1.0 {
		return values[nodeID]
	}

	node := bdd.bddNodes[nodeID]
	variable := bdd.bddVars[node.varid]
	var nodeValue float64
	if !variable.isDecision {
		nodeValue = getValue(bdd, solution, values, node.hi)*variable.pweight +
			getValue(bdd, solution, values, node.lo)*variable.nweight
	} else {
		if solution[variable.id] == true {
			nodeValue = getValue(bdd, solution, values, node.hi) * variable.pweight
		} else {
			nodeValue = getValue(bdd, solution, values, node.lo) * variable.nweight
		}
	}

	values[nodeID] = nodeValue
	return nodeValue
}

func evaluate(bdd BDD, solution map[int]bool) map[int]float64 {
	numberOfNodes := len(bdd.bddNodes)
	values := make([]float64, numberOfNodes)
	for i := 0; i < numberOfNodes; i++ {
		values[i] = -1.0
	}

	rootValues := make(map[int]float64)
	for r := range bdd.roots {
		rootValues[r] = getValue(bdd, solution, values, r)
	}
	return rootValues
}

func increment(assignment []bool) bool {
	hasNext := false
	length := len(assignment)
	for i := 0; i < length && !hasNext; i++ {
		if assignment[i] {
			assignment[i] = false
		} else {
			assignment[i] = true
			hasNext = true
		}
	}
	return hasNext
}

func bruteForce(bdd BDD) {

	assignment := make([]bool, len(bdd.maxVars))
	hasNext := true
	for hasNext {
		solution := make(map[int]bool)
		for i, v := range bdd.maxVars {
			solution[v] = assignment[i]
		}
		for _, v := range bdd.maxVars {
			b := solution[v]
			var a = 0
			if b {
				a = 1
			}
			fmt.Printf("%d:%d ", v, a)
		}
		rootValues := evaluate(bdd, solution)
		fmt.Printf(" --> ")
		total := 0.0
		for r, v := range rootValues {
			fmt.Printf("%d:%.4f\t", r, v)
			total += v
		}
		fmt.Printf("\t%.4f\n", total)
		hasNext = increment(assignment)
	}
}

func main() {
	bddFileName := os.Args[1]
	bdd := readBdd(bddFileName)
	if len(os.Args) == 3 {
		pdfFileName := os.Args[2]
		drawBdd(bdd, pdfFileName)
	} else {
		bruteForce(bdd)
	}
}
