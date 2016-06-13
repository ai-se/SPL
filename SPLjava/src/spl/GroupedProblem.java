package spl;

import org.sat4j.minisat.SolverFactory;
import org.sat4j.minisat.core.IOrder;
import org.sat4j.minisat.core.Solver;
import org.sat4j.minisat.orders.*;
import org.sat4j.reader.DimacsReader;
import org.sat4j.specs.ISolver;
import org.sat4j.tools.ModelIterator;

import java.io.FileReader;
import java.util.Random;
import java.util.ArrayList;
import java.util.Arrays;

/**
 * Created by jianfeng on 6/11/16.
 */
public class GroupedProblem {
    public static void grouping(ProductLineProblem problem, int trigger_size){
        String fm = problem.getFm();
        Random r = new Random();
        boolean[] prod = new boolean[problem.getNumFeatures()];
        for (int i = 0; i < prod.length; i++) {
            prod[i] = r.nextBoolean();

        }
        try {
            IOrder order = new RandomWalkDecorator(new VarOrderHeap(new NegativeLiteralSelectionStrategy()), 1);
            ISolver dimacsSolver = SolverFactory.instance().createSolverByName("MiniSAT");
            dimacsSolver.setTimeout(1000);
            DimacsReader dr = new DimacsReader(dimacsSolver);
            dr.parseInstance(new FileReader(fm));
//
            ((Solver) dimacsSolver).setOrder(order);
            ISolver solverIterator = new ModelIterator(dimacsSolver);
            solverIterator.setTimeoutMs(10000);
            ArrayList<int[]> solutions = new ArrayList();
            int num = 0;
            while (solverIterator.isSatisfiable()) {
                int[] i = solverIterator.model();
                for(int x:i)
                    System.out.print(x>0?'1':'0');
                System.out.println();
                continue;
//                solutions.add(i);
//                if (num++ > trigger_size)
//                    break;
            }

            for (int i = 0; i < solutions.get(0).length; i++){
                int f = solutions.get(0)[i];
                for (int[] x: solutions)
                    if (x[i] != f) {
                        System.out.println(i);
                        break;
                    }

            }

        } catch (Exception e) {
            e.printStackTrace();
        }

    }
}
