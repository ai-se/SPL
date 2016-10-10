package spl;

import org.sat4j.minisat.SolverFactory;
import org.sat4j.minisat.core.IOrder;
import org.sat4j.minisat.core.Solver;
import org.sat4j.minisat.orders.*;
import org.sat4j.reader.DimacsReader;
import org.sat4j.specs.ISolver;
import org.sat4j.tools.ModelIterator;

import java.io.FileReader;
import java.net.URL;
import java.util.Random;

/**
 * Created by jianfeng on 6/19/16.
 */
public class TMP_m {
    public static void main(String[] args) throws Exception{
        String dimacs_file = args[0];
        Random r = new Random();
        boolean[] prod = new boolean[Integer.parseInt(args[1])];
        for (int i = 0; i < prod.length; i++) {
            prod[i] = r.nextBoolean();
        }
        IOrder order = new RandomWalkDecorator(new VarOrderHeap(new RandomLiteralSelectionStrategy()), 1);
        switch (args[2]){
            case "positive":
                order = new RandomWalkDecorator(new VarOrderHeap(new PositiveLiteralSelectionStrategy()), 1);
                break;
            case "negative":
                order = new RandomWalkDecorator(new VarOrderHeap(new NegativeLiteralSelectionStrategy()), 1);
                break;
        }

        ISolver dimacsSolver = SolverFactory.instance().createSolverByName("MiniSAT");
        dimacsSolver.setTimeout(10000000);
        DimacsReader dr = new DimacsReader(dimacsSolver);
        URL location = Main.class.getProtectionDomain().getCodeSource().getLocation();
        String loc = location.toString();
        dr.parseInstance(new FileReader(dimacs_file));
//
        ((Solver) dimacsSolver).setOrder(order);
        ISolver solverIterator = new ModelIterator(dimacsSolver);
        solverIterator.setTimeoutMs(10000000);
        int mode = 3;
        if (args[2].equals("positive"))
            mode = 1;
        if (args[2].equals("negative"))
            mode = 2;
//        while (solverIterator.isSatisfiable()) {
        for (int ew = 0; ew < Integer.parseInt(args[3]); ew ++){
            for (int i = 0; i < prod.length; i++) {
                switch (mode){
                    case 1:
                        prod[i] = true;
                        break;
                    case 2:
                        prod[i] = false;
                        break;
                    default:
                        prod[i] = r.nextBoolean();
                }
            }
            solverIterator.isSatisfiable();
            int[] i = solverIterator.model();
            for (int x : i) {
                if (x > 0)
                    prod[x - 1] = true;
                else
                    prod[-x - 1] = false;
            }
            for (boolean x : prod)
                System.out.print(x ? '1' : '0');
            System.out.println();
        }
    }
}
