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

import java.io.FileReader;
import java.io.File;
import java.io.FileWriter;
import java.io.BufferedWriter;
import java.net.URL;
import java.util.HashSet;
import java.util.List;
import java.util.Random;

import jmetal.core.*;
import jmetal.encodings.variable.Binary;
import org.sat4j.minisat.SolverFactory;
import org.sat4j.minisat.core.IOrder;
import org.sat4j.minisat.core.Solver;
import org.sat4j.minisat.orders.NegativeLiteralSelectionStrategy;
import org.sat4j.minisat.orders.PositiveLiteralSelectionStrategy;
import org.sat4j.minisat.orders.RandomLiteralSelectionStrategy;
import org.sat4j.minisat.orders.RandomWalkDecorator;
import org.sat4j.minisat.orders.VarOrderHeap;
import org.sat4j.reader.DimacsReader;
import org.sat4j.specs.ISolver;
import org.sat4j.specs.IVecInt;
import org.sat4j.tools.ModelIterator;

/**
 *
 * @author chris
 */
public class Main {

    private static Random r = new Random();
    private static final int SATtimeout = 1000;
    private static final long iteratorTimeout = 150000;

    /**
     * @param args the command line arguments -- modelname, alg_name, evaluation_times, [runid]
     */
    public static void main(String[] args) throws Exception {

        try {
            String name = args[0];
            String fm = "/Users/jianfeng/git/SPL/dimacs_data/" + name + ".dimacs";
            String augment = fm + ".augment";
            String dead = fm + ".dead";
            String mandatory = fm + ".mandatory";
            String seed = fm + ".richseed";

            Problem p = new ProductLineProblem(fm, augment, mandatory, dead, seed);
            Algorithm a;

            int evaluation_times = Integer.parseInt(args[2]);
            String alg_name = args[1];
            String runid = "";
            if (args.length >= 4) {
                runid = args[3];
            }
            switch (alg_name){
                case "IBEA":
                    a = new SPL_SettingsIBEA(p).configureICSE2013(evaluation_times);
                    break;
                case "SPEA2":
                    a = new SPL_SettingsEMOs(p).configureSPEA2(evaluation_times);
                    break;
                case "NSGA2":
                    a = new SPL_SettingsEMOs(p).configureNSGA2(evaluation_times);
                    break;
                case "SATIBEA":
                    //a = new SPL_SettingsIBEA(p).configureICSE15(1000, fm, ((ProductLineProblem) p).getNumFeatures(), ((ProductLineProblem) p).getConstraints());
                    a = new SPL_SettingsIBEA(p).configureSATIBEA(evaluation_times, fm, ((ProductLineProblem) p).getNumFeatures(), ((ProductLineProblem) p).getConstraints());
                    break;
                default:
                    a = new SPL_SettingsIBEA(p).configureICSE2013(evaluation_times);
            }

            long start = System.currentTimeMillis();
            SolutionSet pop = a.execute();
            float total_time = (System.currentTimeMillis() - start) / 1000.0f;

            URL location = Main.class.getProtectionDomain().getCodeSource().getLocation();
            String loc = location.toString();

            String file_tag = name + "_" + alg_name + '_' + evaluation_times/1000 + "k_" + runid + ".txt";
            String file_path = (loc.substring(5, loc.lastIndexOf("SPL/"))+"SPL/j_res/" + file_tag);
            File file = new File(file_path);

            if (!file.exists()){
                file.createNewFile();
            }

            FileWriter fw = new FileWriter(file.getAbsoluteFile());
            BufferedWriter bw = new BufferedWriter(fw);

            for (int i = 0; i < pop.size(); i++) {
                Variable v = pop.get(i).getDecisionVariables()[0];
                bw.write((Binary) v + "\n");
                System.out.println("Conf" + (i + 1) + ": " + (Binary) v + " ");

            }

            bw.write("~~~\n");

            for (int i = 0; i < pop.size(); i++) {
                Variable v = pop.get(i).getDecisionVariables()[0];
                for (int j = 0; j < pop.get(i).getNumberOfObjectives(); j++) {
                    bw.write(pop.get(i).getObjective(j) + " ");
                    System.out.print(pop.get(i).getObjective(j) + " ");
                }
                bw.write("\n");
                System.out.println("");
            }

            bw.write("~~~\n" + total_time + "\n");

            bw.close();
            fw.close();

        } catch (Exception e) {
            e.printStackTrace();
//            System.out.println("Usage: java -jar spl.jar fmDimacs timeMS\nThe .augment, .dead, .mandatory and .richseed files should be in the same directory as the FM.");
        }
    }

    public static int numViolatedConstraints(Binary b) {

        //IVecInt v = bitSetToVecInt(b);
        int s = 0;
        for (List<Integer> constraint  : ProductLineProblem.constraints) {
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

    public static int numViolatedConstraints(Binary b, HashSet<Integer> blacklist) {

        //IVecInt v = bitSetToVecInt(b);
        int s = 0;
        for (List<Integer> constraint  : ProductLineProblem.constraints) {
            boolean sat = false;

            for (Integer i : constraint) {
                int abs = (i < 0) ? -i : i;
                boolean sign = i > 0;
                if (b.getIth(abs - 1) == sign) {
                    sat = true;
                } else {
                    blacklist.add(abs);
                }
            }
            if (!sat) {
                s++;
            }

        }

        return s;
    }

    public static int numViolatedConstraints(boolean[] b) {

        //IVecInt v = bitSetToVecInt(b);
        int s = 0;
        for (List<Integer> constraint  : ProductLineProblem.constraints) {

            boolean sat = false;

            for (Integer i : constraint) {
                int abs = (i < 0) ? -i : i;
                boolean sign = i > 0;
                if (b[abs - 1] == sign) {
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

    public boolean[] randomProduct() {

        boolean[] prod = new boolean[ProductLineProblem.numFeatures];
        for (int i = 0; i < prod.length; i++) {
            prod[i] = r.nextBoolean();

        }

        int rand = r.nextInt(3);

        try {
            IOrder order;
            if (rand == 0) {
                order = new RandomWalkDecorator(new VarOrderHeap(new NegativeLiteralSelectionStrategy()), 1);
            } else if (rand == 1) {
                order = new RandomWalkDecorator(new VarOrderHeap(new PositiveLiteralSelectionStrategy()), 1);
            } else {
                order = new RandomWalkDecorator(new VarOrderHeap(new RandomLiteralSelectionStrategy()), 1);
            }

            //dimacsSolver.reset();
            ISolver dimacsSolver2 = SolverFactory.instance().createSolverByName("MiniSAT");
            dimacsSolver2.setTimeout(SATtimeout);

            DimacsReader dr = new DimacsReader(dimacsSolver2);
            dr.parseInstance(new FileReader(ProductLineProblem.fm));
            ((Solver) dimacsSolver2).setOrder(order);

            ISolver solverIterator = new ModelIterator(dimacsSolver2);
            solverIterator.setTimeoutMs(iteratorTimeout);

            if (solverIterator.isSatisfiable()) {
                int[] i = solverIterator.findModel();

                for (int j = 0; j < i.length; j++) {
                    int feat = i[j];

                    int posFeat = feat > 0 ? feat : -feat;

                    if (posFeat > 0) {
                        prod[posFeat - 1] = feat > 0;
                    }

//                    else
//                    {
//                         prod[nFeat-1] = r.nextBoolean();
//                    }
                }

            }

            //solverIterator = null;
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(0);
        }

        return prod;
    }

    public static boolean[] randomProductAssume(IVecInt ivi) {

        boolean[] prod = new boolean[ProductLineProblem.numFeatures];
        for (int i = 0; i < prod.length; i++) {
            prod[i] = r.nextBoolean();

        }

        int rand = r.nextInt(3);

        try {
            IOrder order;
            if (rand == 0) {
                order = new RandomWalkDecorator(new VarOrderHeap(new NegativeLiteralSelectionStrategy()), 1);
            } else if (rand == 1) {
                order = new RandomWalkDecorator(new VarOrderHeap(new PositiveLiteralSelectionStrategy()), 1);
            } else {
                order = new RandomWalkDecorator(new VarOrderHeap(new RandomLiteralSelectionStrategy()), 1);
            }

            //dimacsSolver.reset();
            ISolver dimacsSolver2 = SolverFactory.instance().createSolverByName("MiniSAT");
            dimacsSolver2.setTimeout(SATtimeout);

            DimacsReader dr = new DimacsReader(dimacsSolver2);
            dr.parseInstance(new FileReader(ProductLineProblem.fm));
            ((Solver) dimacsSolver2).setOrder(order);

            ISolver solverIterator = new ModelIterator(dimacsSolver2);
            solverIterator.setTimeoutMs(iteratorTimeout);

            if (solverIterator.isSatisfiable()) {
                int[] i = solverIterator.findModel(ivi);
                for (int j = 0; j < i.length; j++) {
                    int feat = i[j];

                    int posFeat = feat > 0 ? feat : -feat;

                    if (posFeat > 0) {
                        prod[posFeat - 1] = feat > 0;
                    }

//                    else
//                    {
//                         prod[nFeat-1] = r.nextBoolean();
//                    }
                }

            }

            //solverIterator = null;
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(0);
        }

        return prod;
    }

}
