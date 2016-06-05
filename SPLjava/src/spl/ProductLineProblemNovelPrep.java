package spl;

import jmetal.core.Solution;
import jmetal.core.Variable;
import jmetal.encodings.variable.Binary;
import jmetal.util.JMException;

import java.io.BufferedReader;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;
import java.util.StringTokenizer;

/**
 * Created by jianfeng on 6/5/16.
 */

class RestrictNode {
    public ArrayList<Integer> childs;
    public int target;
    public int sum_lower_bound;
    public int sum_upper_bound;

    public RestrictNode(ArrayList childs, int target, int sum_lower_bound, int sum_upper_bound) {
        this.childs = childs;
        this.target = target;
        this.sum_lower_bound = sum_lower_bound;
        this.sum_upper_bound = sum_upper_bound;
    }
}

public class ProductLineProblemNovelPrep extends ProductLineProblem {
    public String opfile;
    private ArrayList<Integer> unzipmap = new ArrayList<Integer>();
    private ArrayList<Integer> manadoryIndices = new ArrayList<Integer>();
    private ArrayList<RestrictNode> rns = new ArrayList<RestrictNode>();

    public ProductLineProblemNovelPrep(String fm, String augment, String mandatory, String dead, String seedfile, String opfile) throws Exception {
        super(fm, augment, mandatory, dead, seedfile);
        this.loadZipOperator(opfile);

        // removing the reasonable targets
        for (RestrictNode rn: rns){
            this.featureIndicesAllowedFlip.remove((Object)rn.target);
        }

    }

    public void loadZipOperator(String opfile) throws Exception {
        BufferedReader in = new BufferedReader(new FileReader(opfile));
        String line = in.readLine();  // first line, the unzip mapping index
        line.trim();
        StringTokenizer st = new StringTokenizer(line, " ");
        while (st.hasMoreTokens()) {
            unzipmap.add(Integer.parseInt(st.nextToken()));
        }

        line = in.readLine(); // second line, the manadoryIndices
        line.trim();
        st = new StringTokenizer(line, " ");
        while (st.hasMoreTokens()) {
            manadoryIndices.add(Integer.parseInt(st.nextToken()));
        }

        // the rest are the formatted structure
        while ((line = in.readLine()) != null) {
            line.trim();
            st = new StringTokenizer(line, " ");
            ArrayList<Integer> tmp = new ArrayList<Integer>();
            while (st.hasMoreTokens()) {
                tmp.add(Integer.parseInt(st.nextToken()));
            }
            int target = tmp.get(tmp.size() - 3);
            int lowerbound = tmp.get(tmp.size() - 2);
            int upperbound = tmp.get(tmp.size() - 1);
            tmp.remove(tmp.size() - 1);
            tmp.remove(tmp.size() - 1);
            tmp.remove(tmp.size() - 1);
            RestrictNode rn = new RestrictNode(tmp, target, lowerbound, upperbound);
            rns.add(rn);
        }
        in.close();
    }



    @Override
    public void evaluate(Solution sltn) throws JMException {
        Variable[] vars = sltn.getDecisionVariables();
        Binary bin = (Binary) vars[0];

        for (RestrictNode rn : rns) {
            int sum = 0;
            for (Integer i: rn.childs){
                if (bin.getIth(i)){
                    sum += 1;
                }
            }
            bin.setIth(rn.target, sum >= rn.sum_lower_bound && sum <= rn.sum_lower_bound);
        }

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
        sltn.setObjective(1, unselected);
        sltn.setObjective(2, unused);
        sltn.setObjective(3, defect);
        sltn.setObjective(4, cost_);
    }
}
