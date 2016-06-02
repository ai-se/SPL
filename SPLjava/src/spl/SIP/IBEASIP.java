/*
 * Author : Jianfeng Chen
 * Date : June 16
 * Copyright 2016 North Carolina State University ai4se.net
 * All rights reserved
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 *  of this software and associated documentation files (the "Software"), to deal
 *  in the Software without restriction, including without limitation the rights
 *  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 *  copies of the Software, and to permit persons to whom the Software is
 *  furnished to do so, subject to the following conditions:

 * The above copyright notice and this permission notice shall be included in
 *  all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 *  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 *  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 *  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 *  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 *  THE SOFTWARE.
 */
package spl.SIP;

import jmetal.core.*;
import jmetal.util.JMException;
import jmetal.util.Ranking;
import jmetal.util.comparators.DominanceComparator;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;

/**
 *
 * @author jiafeng
 */

// TODO to be modified
    
public class IBEASIP extends Algorithm {

    private int print_time = 0;

    private long maxRunTimeMS;

    /**
     * Defines the number of tournaments for creating the mating pool
     */
    public static final int TOURNAMENTS_ROUNDS = 1;

    /**
     * Stores the value of the indicator between each pair of solutions into the
     * solution set
     */
    private List<List<Double>> indicatorValues_;

    /**
     *
     */
    private double maxIndicatorValue_;

    /**
     * Constructor. Create a new IBEA instance
     *
     * @param problem Problem to solve
     */
    public IBEASIP(Problem problem, long maxRunTimeMS) {
        super(problem);
        this.maxRunTimeMS = maxRunTimeMS;
    } // configureSPEA2

//    /**
//     * calculates the hypervolume of that portion of the objective space that is
//     * dominated by individual a but not by individual b
//     */
//    double calcHypervolumeIndicator(Solution p_ind_a,
//            Solution p_ind_b,
//            int d,
//            double maximumValues[],
//            double minimumValues[]) {
//        double a, b, r, max;
//        double volume = 0;
//        double rho = 2.0;
//
//        r = rho * (maximumValues[d - 1] - minimumValues[d - 1]);
//        max = minimumValues[d - 1] + r;
//
//        a = p_ind_a.getObjective(d - 1);
//        if (p_ind_b == null) {
//            b = max;
//        } else {
//            b = p_ind_b.getObjective(d - 1);
//        }
//
//        if (d == 1) {
//            if (a < b) {
//                volume = (b - a) / r;
//            } else {
//                volume = 0;
//            }
//        } else {
//            if (a < b) {
//                volume = calcHypervolumeIndicator(p_ind_a, null, d - 1, maximumValues, minimumValues)
//                        * (b - a) / r;
//                volume += calcHypervolumeIndicator(p_ind_a, p_ind_b, d - 1, maximumValues, minimumValues)
//                        * (max - b) / r;
//            } else {
//                volume = calcHypervolumeIndicator(p_ind_a, p_ind_b, d - 1, maximumValues, minimumValues)
//                        * (max - b) / r;
//            }
//        }
//
//        return (volume);
//    }
//
//    /**
//     * This structure store the indicator values of each pair of elements
//     */
//    public void computeIndicatorValuesHD(SolutionSet solutionSet,
//            double[] maximumValues,
//            double[] minimumValues) {
//        SolutionSet A, B;
//        // Initialize the structures
//        indicatorValues_ = new ArrayList<List<Double>>();
//        maxIndicatorValue_ = -Double.MAX_VALUE;
//
//        for (int j = 0; j < solutionSet.size(); j++) {
//            A = new SolutionSet(1);
//            A.add(solutionSet.get(j));
//
//            List<Double> aux = new ArrayList<Double>();
//            for (int i = 0; i < solutionSet.size(); i++) {
//                B = new SolutionSet(1);
//                B.add(solutionSet.get(i));
//
//                int flag = (new DominanceComparator()).compare(A.get(0), B.get(0));
//
//                double value = 0.0;
//                if (flag == -1) {
//                    value = -calcHypervolumeIndicator(A.get(0), B.get(0), problem_.getNumberOfObjectives(), maximumValues, minimumValues);
//                } else {
//                    value = calcHypervolumeIndicator(B.get(0), A.get(0), problem_.getNumberOfObjectives(), maximumValues, minimumValues);
//                }
//        //double value = epsilon.epsilon(matrixA,matrixB,problem_.getNumberOfObjectives());
//
//                //Update the max value of the indicator
//                if (Math.abs(value) > maxIndicatorValue_) {
//                    maxIndicatorValue_ = Math.abs(value);
//                }
//                aux.add(value);
//            }
//            indicatorValues_.add(aux);
//        }
//    } // computeIndicatorValues
//
//    /**
//     * Calculate the fitness for the individual at position pos
//     */
//    public void fitness(SolutionSet solutionSet, int pos) {
//        double fitness = 0.0;
//        double kappa = 0.05;
//
//        for (int i = 0; i < solutionSet.size(); i++) {
//            if (i != pos) {
//                fitness += Math.exp((-1 * indicatorValues_.get(i).get(pos) / maxIndicatorValue_) / kappa);
//            }
//        }
//        if (solutionSet.get(pos).getObjective(0) > 0) {
//            solutionSet.get(pos).setFitness(Double.MAX_VALUE);
//        } else {
//            solutionSet.get(pos).setFitness(fitness);
//        }
//    }
//
//    /**
//     * Calculate the fitness for the entire population.
//     *
//     */
//    public void calculateFitness(SolutionSet solutionSet) {
//        // Obtains the lower and upper bounds of the population
//        double[] maximumValues = new double[problem_.getNumberOfObjectives()];
//        double[] minimumValues = new double[problem_.getNumberOfObjectives()];
//
//        for (int i = 0; i < problem_.getNumberOfObjectives(); i++) {
//            maximumValues[i] = -Double.MAX_VALUE; // i.e., the minus maxium value
//            minimumValues[i] = Double.MAX_VALUE; // i.e., the maximum value
//        }
//
//        for (int pos = 0; pos < solutionSet.size(); pos++) {
//            for (int obj = 0; obj < problem_.getNumberOfObjectives(); obj++) {
//                double value = solutionSet.get(pos).getObjective(obj);
//                if (value > maximumValues[obj]) {
//                    maximumValues[obj] = value;
//                }
//                if (value < minimumValues[obj]) {
//                    minimumValues[obj] = value;
//                }
//            }
//        }
//
//        computeIndicatorValuesHD(solutionSet, maximumValues, minimumValues);
//        for (int pos = 0; pos < solutionSet.size(); pos++) {
//            fitness(solutionSet, pos);
//        }
//    }
//
//    /**
//     * Update the fitness before removing an individual
//     */
//    public void removeWorst(SolutionSet solutionSet) {
//
//        // Find the worst;
//        double worst = solutionSet.get(0).getFitness();
//        int worstIndex = 0;
//        double kappa = 0.05;
//
//        for (int i = 1; i < solutionSet.size(); i++) {
//            if (solutionSet.get(i).getFitness() > worst) {
//                worst = solutionSet.get(i).getFitness();
//                worstIndex = i;
//            }
//        }
//
//        //if (worstIndex == -1) {
//        //    System.out.println("Yes " + worst);
//        //}
//        //System.out.println("Solution Size "+solutionSet.size());
//        //System.out.println(worstIndex);
//        // Update the population
//        for (int i = 0; i < solutionSet.size(); i++) {
//            if (i != worstIndex) {
//                double fitness = solutionSet.get(i).getFitness();
//                fitness -= Math.exp((-indicatorValues_.get(worstIndex).get(i) / maxIndicatorValue_) / kappa);
//                if (solutionSet.get(i).getObjective(0) > 0) {
//                    solutionSet.get(i).setFitness(Double.MAX_VALUE);
//                } else {
//                    solutionSet.get(i).setFitness(fitness);
//                }
//            }
//        }
//
//        // remove worst from the indicatorValues list
//        indicatorValues_.remove(worstIndex); // Remove its own list
//        Iterator<List<Double>> it = indicatorValues_.iterator();
//        while (it.hasNext()) {
//            it.next().remove(worstIndex);
//        }
//
//        // remove the worst individual from the population
////        if (solutionSet.get(worstIndex).getObjective(0) == 0){
////        System.out.print("Removed: ");
////        Variable v = solutionSet.get(worstIndex).getDecisionVariables()[0];
////        for (int j = 0; j < solutionSet.get(worstIndex).getNumberOfObjectives(); j++) {
////            System.out.print(solutionSet.get(worstIndex).getObjective(j) + " ");
////        }
////        System.out.println("");
////        }
//        solutionSet.remove(worstIndex);
//    } // removeWorst
    /**
     * calculates the hypervolume of that portion of the objective space that is
     * dominated by individual a but not by individual b
     */
    double calcHypervolumeIndicator(Solution p_ind_a,
            Solution p_ind_b,
            int d,
            double maximumValues[],
            double minimumValues[]) {
        double a, b, r, max;
        double volume = 0;
        double rho = 2.0;

        r = rho * (maximumValues[d - 1] - minimumValues[d - 1]);
        max = minimumValues[d - 1] + r;

        a = p_ind_a.getObjective(d - 1);
        if (p_ind_b == null) {
            b = max;
        } else {
            b = p_ind_b.getObjective(d - 1);
        }

        if (d == 1) {
            if (a < b) {
                volume = (b - a) / r;
            } else {
                volume = 0;
            }
        } else {
            if (a < b) {
                volume = calcHypervolumeIndicator(p_ind_a, null, d - 1, maximumValues, minimumValues)
                        * (b - a) / r;
                volume += calcHypervolumeIndicator(p_ind_a, p_ind_b, d - 1, maximumValues, minimumValues)
                        * (max - b) / r;
            } else {
                volume = calcHypervolumeIndicator(p_ind_a, p_ind_b, d - 1, maximumValues, minimumValues)
                        * (max - b) / r;
            }
        }

        return (volume);
    }

    /**
     * This structure store the indicator values of each pair of elements
     */
    public void computeIndicatorValuesHD(SolutionSet solutionSet,
            double[] maximumValues,
            double[] minimumValues) {
        SolutionSet A, B;
        // Initialize the structures
        indicatorValues_ = new ArrayList<List<Double>>();
        maxIndicatorValue_ = -Double.MAX_VALUE;

        for (int j = 0; j < solutionSet.size(); j++) {
            A = new SolutionSet(1);
            A.add(solutionSet.get(j));

            List<Double> aux = new ArrayList<Double>();
            for (int i = 0; i < solutionSet.size(); i++) {
                B = new SolutionSet(1);
                B.add(solutionSet.get(i));

                int flag = (new DominanceComparator()).compare(A.get(0), B.get(0));

                double value = 0.0;
                if (flag == -1) {
                    value = -calcHypervolumeIndicator(A.get(0), B.get(0), problem_.getNumberOfObjectives(), maximumValues, minimumValues);
                } else {
                    value = calcHypervolumeIndicator(B.get(0), A.get(0), problem_.getNumberOfObjectives(), maximumValues, minimumValues);
                }
        //double value = epsilon.epsilon(matrixA,matrixB,problem_.getNumberOfObjectives());

                //Update the max value of the indicator
                if (Math.abs(value) > maxIndicatorValue_) {
                    maxIndicatorValue_ = Math.abs(value);
                }
                aux.add(value);
            }
            indicatorValues_.add(aux);
        }
    } // computeIndicatorValues

    /**
     * Calculate the fitness for the individual at position pos
     */
    public void fitness(SolutionSet solutionSet, int pos) {
        double fitness = 0.0;
        double kappa = 0.05;

        for (int i = 0; i < solutionSet.size(); i++) {
            if (i != pos) {
                fitness += Math.exp((-1 * indicatorValues_.get(i).get(pos) / maxIndicatorValue_) / kappa);
            }
        }

        solutionSet.get(pos).setFitness(fitness);

    }

    /**
     * Calculate the fitness for the entire population.
     *
     */
    public void calculateFitness(SolutionSet solutionSet) {
        // Obtains the lower and upper bounds of the population
        double[] maximumValues = new double[problem_.getNumberOfObjectives()];
        double[] minimumValues = new double[problem_.getNumberOfObjectives()];

        for (int i = 0; i < problem_.getNumberOfObjectives(); i++) {
            maximumValues[i] = -Double.MAX_VALUE; // i.e., the minus maxium value
            minimumValues[i] = Double.MAX_VALUE; // i.e., the maximum value
        }

        for (int pos = 0; pos < solutionSet.size(); pos++) {
            for (int obj = 0; obj < problem_.getNumberOfObjectives(); obj++) {
                double value = solutionSet.get(pos).getObjective(obj);
                if (value > maximumValues[obj]) {
                    maximumValues[obj] = value;
                }
                if (value < minimumValues[obj]) {
                    minimumValues[obj] = value;
                }
            }
        }

        computeIndicatorValuesHD(solutionSet, maximumValues, minimumValues);
        for (int pos = 0; pos < solutionSet.size(); pos++) {
            fitness(solutionSet, pos);
        }
    }

    /**
     * Update the fitness before removing an individual
     */
    public void removeWorst(SolutionSet solutionSet) {

        // Find the worst;
        double worst = solutionSet.get(0).getFitness();
        int worstIndex = 0;
        double kappa = 0.05;

        for (int i = 1; i < solutionSet.size(); i++) {
            if (solutionSet.get(i).getFitness() > worst) {
                worst = solutionSet.get(i).getFitness();
                worstIndex = i;
            }
        }

        //if (worstIndex == -1) {
        //    System.out.println("Yes " + worst);
        //}
        //System.out.println("Solution Size "+solutionSet.size());
        //System.out.println(worstIndex);
        // Update the population
        for (int i = 0; i < solutionSet.size(); i++) {
            if (i != worstIndex) {
                double fitness = solutionSet.get(i).getFitness();
                fitness -= Math.exp((-indicatorValues_.get(worstIndex).get(i) / maxIndicatorValue_) / kappa);
                solutionSet.get(i).setFitness(fitness);
            }
        }

        // remove worst from the indicatorValues list
        indicatorValues_.remove(worstIndex); // Remove its own list
        Iterator<List<Double>> it = indicatorValues_.iterator();
        while (it.hasNext()) {
            it.next().remove(worstIndex);
        }

        // remove the worst individual from the population
        if (solutionSet.get(worstIndex).getObjective(0) == 0) {
            System.out.print("Removed-" + print_time + "-: ");
            Variable v = solutionSet.get(worstIndex).getDecisionVariables()[0];
            for (int j = 0; j < solutionSet.get(worstIndex).getNumberOfObjectives(); j++) {
                System.out.print(solutionSet.get(worstIndex).getObjective(j) + " ");
            }
            System.out.println("");
        }
        solutionSet.remove(worstIndex);
    } // removeWorst

    /**
     * Runs of the IBEA algorithm.
     *
     * @return a <code>SolutionSet</code> that is a set of non dominated
     * solutions as a result of the algorithm execution
     * @throws JMException
     */
    public SolutionSet execute() throws JMException, ClassNotFoundException {

        long elapsed = 0, last = 0, start = System.currentTimeMillis();

        int populationSize, archiveSize, maxEvaluations, evaluations;
        Operator crossoverOperator, mutationOperator, selectionOperator;
        SolutionSet solutionSet, archive, offSpringSolutionSet;

        //Read the params
        populationSize = ((Integer) getInputParameter("populationSize")).intValue();
        archiveSize = ((Integer) getInputParameter("archiveSize")).intValue();
        maxEvaluations = ((Integer) getInputParameter("maxEvaluations")).intValue();

        //Read the operators
        crossoverOperator = operators_.get("crossover");
        mutationOperator = operators_.get("mutation");
        selectionOperator = operators_.get("selection");

        //Initialize the variables
        solutionSet = new SolutionSet(populationSize);
        archive = new SolutionSet(archiveSize);
        evaluations = 0;

        //-> Create the initial solutionSet
        Solution newSolution;
        for (int i = 0; i < populationSize; i++) {
            newSolution = new Solution(problem_);
            problem_.evaluate(newSolution);
            problem_.evaluateConstraints(newSolution);
            evaluations++;
            solutionSet.add(newSolution);
        }

        //for the time
//        for (int i = 0; i < solutionSet.size(); i++) {
//            System.out.print("Sol" + i + "-" + print_time + "-: ");
//            for (int j = 0; j < solutionSet.get(i).getNumberOfObjectives(); j++) {
//                System.out.print(solutionSet.get(i).getObjective(j) + " ");
//            }
//            System.out.println("");
//        }

        while (elapsed < this.maxRunTimeMS) {

            //while (evaluations < maxEvaluations){
            SolutionSet union = ((SolutionSet) solutionSet).union(archive);
            calculateFitness(union);
            archive = union;

            while (archive.size() > populationSize) {
                removeWorst(archive);
            }
            // Create a new offspringPopulation
            offSpringSolutionSet = new SolutionSet(populationSize);
            Solution[] parents = new Solution[2];
            while (offSpringSolutionSet.size() < populationSize) {
                int j = 0;
                do {
                    j++;
                    parents[0] = (Solution) selectionOperator.execute(archive);
                } while (j < IBEASIP.TOURNAMENTS_ROUNDS); // do-while
                int k = 0;
                do {
                    k++;
                    parents[1] = (Solution) selectionOperator.execute(archive);
                } while (k < IBEASIP.TOURNAMENTS_ROUNDS); // do-while

                //make the crossover
                Solution[] offSpring = (Solution[]) crossoverOperator.execute(parents);
                mutationOperator.execute(offSpring[0]);
                problem_.evaluate(offSpring[0]);
                problem_.evaluateConstraints(offSpring[0]);
                offSpringSolutionSet.add(offSpring[0]);
                evaluations++;
            } // while
            // End Create a offSpring solutionSet
            solutionSet = offSpringSolutionSet;

            elapsed = System.currentTimeMillis() - start;

            //for the time
//            if (System.currentTimeMillis() - last >= 60000) {
//                last = System.currentTimeMillis();
//                print_time++;
//                for (int i = 0; i < solutionSet.size(); i++) {
//                    System.out.print("Sol" + i + "-" + print_time + "-: ");
//                    for (int j = 0; j < solutionSet.get(i).getNumberOfObjectives(); j++) {
//                        System.out.print(solutionSet.get(i).getObjective(j) + " ");
//                    }
//                    System.out.println("");
//                }
//
//            }
        } // while

        
        
        
        //for time print only
//        print_time=30;
//        for (int i = 0; i < solutionSet.size(); i++) {
//            System.out.print("Sol" + i + "-" + print_time + "-: ");
//            for (int j = 0; j < solutionSet.get(i).getNumberOfObjectives(); j++) {
//                System.out.print(solutionSet.get(i).getObjective(j) + " ");
//            }
//            System.out.println("");
//        }
        
        
        
        
        
        
        

        System.out.println("RunTimeMS: " + this.maxRunTimeMS);
        System.out.println("Evaluations: " + evaluations);

        Ranking ranking = new Ranking(archive);
        return ranking.getSubfront(0);
    } // execute
} // configureSPEA2
