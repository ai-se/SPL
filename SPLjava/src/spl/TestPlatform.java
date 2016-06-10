package spl;

import jmetal.core.*;
import jmetal.encodings.solutionType.BinarySolutionType;
import jmetal.encodings.variable.Binary;
import jmetal.util.JMException;
import jmetal.util.Ranking;
import jmetal.util.comparators.DominanceComparator;
import org.sat4j.minisat.SolverFactory;
import org.sat4j.reader.DimacsReader;
import org.sat4j.specs.ISolver;
import org.sat4j.tools.ModelIterator;

import java.io.FileReader;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;


public class TestPlatform extends Algorithm {

    private int print_time = 0;

    private long maxRunTimeMS=1000;

//    Binary[] x;
    BinarySolutionType[] x;

    public TestPlatform(Problem problem, long maxRunTimeMS) throws Exception {
        super(problem);
        this.maxRunTimeMS = maxRunTimeMS;
         x = randomProductSet(1000);
    } // configureSPEA2

    public  static Binary[] randomProductSet(int requries) throws Exception{
        ISolver dimacsSolver = SolverFactory.instance().createSolverByName("MiniSAT");
        dimacsSolver.setTimeout(150);
        DimacsReader dr = new DimacsReader(dimacsSolver);
        dr.parseInstance(new FileReader(ProductLineProblem.fm));

        ModelIterator solverIterator = new ModelIterator(dimacsSolver);

        int t = 0;
        Binary[] res = new Binary[requries];
        while (solverIterator.isSatisfiable()){
            int[] i = solverIterator.model();
            Binary x = new Binary(i.length);
            for (int t_i = 0; t_i < i.length; t_i++)
                x.setIth(t_i, i[t_i]>0);
            res[t] = x;
            if (t ++> requries)
                break;
        }
        return res;
    }


    public SolutionSet execute() throws JMException, ClassNotFoundException {
        Solution xx = new Solution(this.problem_, x);

        return null;
    }
//    public SolutionSet execute() throws JMException, ClassNotFoundException {
//
//        long elapsed = 0, last = 0, start = System.currentTimeMillis();
//
//        int populationSize, archiveSize, maxEvaluations, evaluations;
//        Operator crossoverOperator, mutationOperator, selectionOperator;
//        SolutionSet solutionSet, archive, offSpringSolutionSet;
//
//        //Read the params
//        populationSize = ((Integer) getInputParameter("populationSize")).intValue();
//        archiveSize = ((Integer) getInputParameter("archiveSize")).intValue();
//        maxEvaluations = ((Integer) getInputParameter("maxEvaluations")).intValue();
//
//        //Read the operators
//        crossoverOperator = operators_.get("crossover");
//        mutationOperator = operators_.get("mutation");
//        selectionOperator = operators_.get("selection");
//
//        //Initialize the variables
//        solutionSet = new SolutionSet(populationSize);
//        archive = new SolutionSet(archiveSize);
//        evaluations = 0;
//
//        //-> Create the initial solutionSet
//        Solution newSolution;
//        for (int i = 0; i < populationSize; i++) {
//            newSolution = new Solution(problem_);
//            problem_.evaluate(newSolution);
//            problem_.evaluateConstraints(newSolution);
//            evaluations++;
//            solutionSet.add(newSolution);
//        }
//
//
//        while (elapsed < this.maxRunTimeMS) {
//
//            //while (evaluations < maxEvaluations){
//            SolutionSet union = ((SolutionSet) solutionSet).union(archive);
//            calculateFitness(union);
//            archive = union;
//
//            while (archive.size() > populationSize) {
//                removeWorst(archive);
//            }
//            // Create a new offspringPopulation
//            offSpringSolutionSet = new SolutionSet(populationSize);
//            Solution[] parents = new Solution[2];
//            while (offSpringSolutionSet.size() < populationSize) {
//                int j = 0;
//                do {
//                    j++;
//                    parents[0] = (Solution) selectionOperator.execute(archive);
//                } while (j < TestPlatform.TOURNAMENTS_ROUNDS); // do-while
//                int k = 0;
//                do {
//                    k++;
//                    parents[1] = (Solution) selectionOperator.execute(archive);
//                } while (k < TestPlatform.TOURNAMENTS_ROUNDS); // do-while
//
//                //make the crossover
//                Solution[] offSpring = (Solution[]) crossoverOperator.execute(parents);
//                mutationOperator.execute(offSpring[0]);
//                problem_.evaluate(offSpring[0]);
//                problem_.evaluateConstraints(offSpring[0]);
//                offSpringSolutionSet.add(offSpring[0]);
//                evaluations++;
//            } // while
//            // End Create a offSpring solutionSet
//            solutionSet = offSpringSolutionSet;
//
//            elapsed = System.currentTimeMillis() - start;
//
//        } // while
//
//
//        System.out.println("RunTimeMS: " + this.maxRunTimeMS);
//        System.out.println("Evaluations: " + evaluations);
//
//        Ranking ranking = new Ranking(archive);
//        return ranking.getSubfront(0);
//    } // execute
}
