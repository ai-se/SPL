/*
 * Author : Christopher Henard (christopher.henard@uni.lu)
 * Date : 01/03/14
 * Copyright 2013 University of Luxembourg – Interdisciplinary Centre for Security Reliability and Trust (SnT)
 * All rights reserved
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package spl;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;
import java.util.Arrays;
import java.util.StringTokenizer;
import java.util.stream.IntStream;

import jmetal.core.Problem;
import jmetal.core.Solution;
import jmetal.core.Variable;
import jmetal.encodings.variable.Binary;
import jmetal.util.JMException;

/**
 *
 * @author chris
 */
public class ProductLineProblem extends Problem {

    public static String fm;
    protected String augment;
    public static int numFeatures;
    protected int numConstraints;
    public static List<List<Integer>> constraints;
    private float[] constraintWeight;
    protected double[] cost;
    protected boolean[] used_before;
    protected int[] defects;
    protected static int n = 0;
    protected List<Integer> mandatoryFeaturesIndices, deadFeaturesIndices;
    public static List<Integer> featureIndicesAllowedFlip;
    protected List<Integer> seed;

    
    protected static final int N_VARS = 1, N_OBJS = 5;

//    public ProductLineProblem(){
//
//    }

    public ProductLineProblem(String fm, String augment, String mandatory, String dead, String seedfile) throws Exception {
        this.numberOfVariables_ = N_VARS;
        this.numberOfObjectives_ = N_OBJS;
        this.numberOfConstraints_ = 0;
        this.fm = fm;
        this.augment = augment;
        loadFM(fm, augment);
        loadMandatoryDeadFeaturesIndices(mandatory, dead);
        loadSeed(seedfile);

        constraintWeight = new float[constraints.size()];
        Arrays.fill(constraintWeight, 1f);

        this.solutionType_ = new SPL_BinarySolution(this, numFeatures, fm,mandatoryFeaturesIndices, deadFeaturesIndices, seed);
    }

    public List<List<Integer>> getConstraints() {
        return constraints;
    }

    @Override
    public void evaluate(Solution sltn) throws JMException {
        Variable[] vars = sltn.getDecisionVariables();
        Binary bin = (Binary) vars[0];

        int unselected = 0, unused = 0, defect = 0;
        double cost_ = 0.0;

        for (int i = 0; i < bin.getNumberOfBits(); i++) {

            boolean b = bin.getIth(i);

            if (!b) {
                unselected++;
            } else {
                cost_ += cost[i];
                if (used_before[i]) {
                    defect += defects[i];
                } else {
                    unused++;
                }
            }

        }
        sltn.setObjective(0, numViolatedConstraints(bin));
//        sltn.setObjective(0, weightedViolatedConstraints(bin));
        sltn.setObjective(1, unselected);
        sltn.setObjective(2, unused);
        sltn.setObjective(3, defect);
        sltn.setObjective(4, cost_);
    }

    public String getFm() {
        return fm;
    }

    public int getNumFeatures() {
        return numFeatures;
    }

//    public void updateConstraintWeight(Binary[] bs){
//        int[] counter = new int[constraints.size()];
//        for (Binary b: bs){
//            ArrayList<Integer> tmp = violatedConstraintsIndex(b);
//            for (int i: tmp){
//                counter[i] += 1;
//            }
//        }
//        int sum = Arrays.stream(counter).sum();
//        for (int i = 0; i < this.constraintWeight.length; i ++){
//            constraintWeight[i] = (0f + counter[i]) / sum * constraints.size();
//        }
//    }
    
    
    public int numViolatedConstraints(Binary b) {

        //IVecInt v = bitSetToVecInt(b);
        int s = 0;
        for (List<Integer> constraint : constraints) {
            boolean sat = false;

            for (Integer i : constraint) {
                int abs = (i < 0) ? -i : i;
                boolean sign = i > 0;
                if (b.getIth(abs - 1) == sign) {
                    sat = true;
                    break;
                }
            }
            if (!sat) {
                s++;
            }

        }

        return s;
    }

//    public float weightedViolatedConstraints(Binary b) {
//
//        //IVecInt v = bitSetToVecInt(b);
//        float s = 0f;
////        for (List<Integer> constraint : constraints) {
//        for (int index = 0; index < constraints.size(); index++){
//            List<Integer> constraint = constraints.get(index);
//            boolean sat = false;
//
//            for (Integer i : constraint) {
//                int abs = (i < 0) ? -i : i;
//                boolean sign = i > 0;
//                if (b.getIth(abs - 1) == sign) {
//                    sat = true;
//                    break;
//                }
//            }
//            if (!sat) {
//                s += constraintWeight[index];
//            }
//
//        }
//
//        return s;
//    }


    public ArrayList<Integer> violatedConstraintsIndex(Binary b){
        ArrayList<Integer> res = new ArrayList<>();
        for (int index = 0; index < constraints.size(); index++){
            List<Integer> constraint = constraints.get(index);
            boolean sat = false;
            for (Integer i: constraint){
                int abs = (i < 0) ? -i: i;
                boolean sign = i > 0;
                if (b.getIth(abs - 1) == sign) {
                    sat = true;
                    break;
                }
            }
            if (!sat){
                res.add(index);
            }
        }
        return res;
    }

    public void loadFM(String fm, String augment) throws Exception {
        BufferedReader in = new BufferedReader(new FileReader(fm));
        String line;
        while ((line = in.readLine()) != null) {
            line = line.trim();

            if (line.startsWith("p")) {
                StringTokenizer st = new StringTokenizer(line, " ");
                st.nextToken();
                st.nextToken();
                numFeatures = Integer.parseInt(st.nextToken());
                numConstraints = Integer.parseInt(st.nextToken());
                constraints = new ArrayList<List<Integer>>(numConstraints);
            }

            if (!line.startsWith("c") && !line.startsWith("p") && !line.isEmpty()) {
                StringTokenizer st = new StringTokenizer(line, " ");
                List<Integer> constraint = new ArrayList<Integer>(st.countTokens() - 1);

                while (st.hasMoreTokens()) {
                    int i = Integer.parseInt(st.nextToken());
                    if (i != 0) {
                        constraint.add(i);
                    }
                }
                constraints.add(constraint);
            }
        }
        in.close();

        cost = new double[numFeatures];
        used_before = new boolean[numFeatures];
        defects = new int[numFeatures];

        in = new BufferedReader(new FileReader(augment));
        while ((line = in.readLine()) != null) {
            line = line.trim();
            if (!line.startsWith("#")) {
                StringTokenizer st = new StringTokenizer(line, " ");
                int featIndex = Integer.parseInt(st.nextToken()) - 1;
                cost[featIndex] = Double.parseDouble(st.nextToken());
                used_before[featIndex] = Integer.parseInt(st.nextToken()) == 1;
                defects[featIndex] = Integer.parseInt(st.nextToken());
            }
        }
    }

    public void loadMandatoryDeadFeaturesIndices(String mandatory, String dead) throws Exception {

        mandatoryFeaturesIndices = new ArrayList<Integer>(numFeatures);
        deadFeaturesIndices = new ArrayList<Integer>(numFeatures);
        featureIndicesAllowedFlip = new ArrayList<Integer>(numFeatures);
        
       

        BufferedReader in = new BufferedReader(new FileReader(mandatory));
        String line;
        while ((line = in.readLine()) != null) {
            if (!line.isEmpty()) {
                int i = Integer.parseInt(line) - 1;
                mandatoryFeaturesIndices.add(i);
            }

        }
        in.close();
        
        in = new BufferedReader(new FileReader(dead));
        while ((line = in.readLine()) != null) {
            if (!line.isEmpty()) {
                int i = Integer.parseInt(line) - 1;
                deadFeaturesIndices.add(i);

            }

        }
        in.close();
        
         for (int i = 0; i < numFeatures; i++) {
            if (! mandatoryFeaturesIndices.contains(i) && !deadFeaturesIndices.contains(i))
                featureIndicesAllowedFlip.add(i);
            
        }

    }
    
    public void loadSeed(String seedfile) throws Exception{

        seed = new ArrayList<Integer>(numFeatures);
        
        Binary bin = new Binary(numFeatures);
        
        BufferedReader in = new BufferedReader(new FileReader(seedfile));
        String line;
        while ((line = in.readLine()) != null) {
            line.trim();
            StringTokenizer st = new StringTokenizer(line, " ");
            while(st.hasMoreElements()){
                int i = Integer.parseInt(st.nextToken());
                seed.add(i);
            }
        }

        in.close();
    }

}
