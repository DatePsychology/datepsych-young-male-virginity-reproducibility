import csv, json, unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
def rows(path):
    with (P/path).open(encoding='utf-8-sig',newline='') as f: return list(csv.DictReader(f))
class AggregateChecks(unittest.TestCase):
    def test_chronology(self):
        a={r['category']:r for r in rows('figure_data/chronology_components.csv')}
        exclusive=[r for k,r in a.items() if k not in ('adult_known_yes_vaginal','adult_known_any_vaginal_status')]
        self.assertEqual(len(exclusive),6);self.assertEqual(sum(int(r['n_event']) for r in exclusive),938)
        self.assertAlmostEqual(sum(float(r['share']) for r in exclusive),1,places=8)
        self.assertAlmostEqual(float(a['reported_age_strictly_after_y15']['share'])*100,48.52,places=2)
        self.assertEqual(sum(int(a[k]['n_event']) for k in ['reported_age_strictly_after_y15','reported_age_earlier_than_y15','reported_same_completed_age','adult_vaginal_yes_age_missing']),514)
    def test_vaginal_audit(self):
        j=json.loads((P/'aggregate_results/audit_validation.json').read_text());self.assertTrue(all(j['historical_checks'].values()));self.assertEqual(len(j['historical_checks']),12)
        self.assertEqual((j['target_n'],j['observed_n'],j['positive_n'],j['weight_replicates']),(938,697,514,33))
        a={r['specification']:r for r in rows('aggregate_results/vaginal_weight_sensitivity.csv')};self.assertEqual(len(a),13)
        self.assertAlmostEqual(float(a['cc_original']['estimate_pct']),75.30,places=2);self.assertAlmostEqual(float(a['ipw_original']['estimate_pct']),74.96,places=2)
        for k,r in a.items():
            self.assertEqual(int(r['replicates_valid']),33)
            self.assertLessEqual(float(r['ci95_low_pct']),float(r['estimate_pct']));self.assertGreaterEqual(float(r['ci95_high_pct']),float(r['estimate_pct']))
            if 'cap' in k: self.assertLess(abs(float(r['delta_vs_baseline_pp'])),1.5)
            if r['comparison_baseline'] in a:
                self.assertAlmostEqual(float(r['estimate_pct'])-float(a[r['comparison_baseline']]['estimate_pct']),float(r['delta_vs_baseline_pp']),delta=.021)
    def test_weight_concentration(self):
        a={r['specification']:r for r in rows('aggregate_results/vaginal_weight_concentration.csv')}
        self.assertAlmostEqual(float(a['cc_original']['kish_ess']),132.87,places=2);self.assertAlmostEqual(float(a['ipw_original']['kish_ess']),146.93,places=2)
        for r in a.values(): self.assertLess(float(r['top_1pct_weight_share_pct']),float(r['top_5pct_weight_share_pct']))
    def test_yrbs(self):
        a={int(r['year']):r for r in rows('figure_data/yrbs_missingness_sensitivity.csv') if r['population']=='boys_all'}
        self.assertAlmostEqual((float(a[2019]['complete_case'])-float(a[2011]['complete_case']))*100,-9.97,places=2)
        m={int(r['year']):r for r in rows('analyses/yrbs_nsfg/output/yrbs_missingness_age_grade_MNAR.csv')}
        for yr,expected in [(2011,49.1),(2019,39.3)]:self.assertAlmostEqual(float(m[yr]['age_grade_MAR'])*100,expected,places=1)
    def test_thresholds(self):
        a={int(r['threshold']):r for r in rows('analyses/nsfg_fixed_cohort/output/same_cohort_fixed_milestone_contrasts.csv') if r['cohort']=='1985–89' and r['pop']=='all men' and r['old']=='2017_2019' and r['new']=='2022_2023'}
        for age,value in [(18,13.45),(21,16.54),(25,10.35)]:self.assertAlmostEqual(float(a[age]['difference_pp']),value,places=2)
    def test_figures(self):
        a={p.name for p in (P/'article_figures').glob('*.png')};b={p.name for p in (P/'reproduced_figures').glob('*.png')};self.assertEqual(len(a),9);self.assertEqual(a,b)
if __name__=='__main__':unittest.main()
