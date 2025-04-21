"""

"""
import pandas as pd
import scipy.stats as stats


def label_p_value(p):
    if p <= 0.01:
        return '***'
    elif 0.01 < p <= 0.05:
        return '**'
    elif 0.05 < p <= 0.1:
        return '*'
    else:
        return ''
    

def main():
    high_pollution = pd.read_excel('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/car data/high_pollution_event.xlsx')
    low_pollution = pd.read_excel('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/car data/low_pollution_event.xlsx')
    high_esg_score = pd.read_excel('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/car data/high_esg_score.xlsx')
    low_esg_score = pd.read_excel('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/car data/low_esg_score.xlsx')
    before_cop = pd.read_excel('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/car data/before_cop.xlsx')
    after_cop = pd.read_excel('/Users/alex/Desktop/0511assay data測試/124 sample/analysis data/分類data/car data/after_cop.xlsx')



    pollution_result = pd.DataFrame(columns=['test statistic', 'p value', 'significance'])
    esg_score_result = pd.DataFrame(columns=['test statistic', 'p value', 'significance'])
    esg_levene = pd.DataFrame(columns=['test statistic', 'p value', 'significance'])
    cop = pd.DataFrame(columns=['test statistic', 'p value', 'significance'])
    cop_levene = pd.DataFrame(columns=['test statistic', 'p value', 'significance'])
    

    for i, column in enumerate(high_pollution.columns):

        # 檢定高污染or低污染產業
        stat1, p1 = stats.mannwhitneyu(high_pollution[column].dropna(), low_pollution[column].dropna())
        significance1 = label_p_value(p1)
        pollution_result.loc[i] = [round(stat1, 3), round(p1, 3), significance1]


        # 檢定ESG rating高低
        # 同質變異數檢測
        stats_l1, p_l1 = stats.levene(high_esg_score[column].dropna(), low_esg_score[column].dropna())
        sig1 = label_p_value(p_l1)
        esg_levene.loc[i] = [round(stats_l1, 3), round(p_l1, 3), sig1]

        # 若levene顯著要進行weich自由度修正t test：須根據你檢測顯著的窗格進行修改 ＆ equal_var設定False！
        if column == ['car[-2 +2]', 'car[-3 +3]', 'car[-10 +10]']:
            # 獨立兩樣本 welch自由度修正 t test
            stat2, p2 = stats.ttest_ind(high_esg_score[column].dropna(), low_esg_score[column].dropna(), equal_var=False)
            significance2 = label_p_value(p2)
            esg_score_result.loc[i] = [round(stat2, 3), round(p2, 3), significance2]

        # 若levene不顯著則執行一般t test ＆ equal_var設定True
        else:
            # 獨立兩樣本一般 t test
            stat2, p2 = stats.ttest_ind(high_esg_score[column].dropna(), low_esg_score[column].dropna(), equal_var=True)
            significance2 = label_p_value(p2)
            esg_score_result.loc[i] = [round(stat2, 3), round(p2, 3), significance2]


        # 檢定事件日於COP 第26次會議前or後
        # 同質變異數檢測
        stats_l2, p_l2 = stats.levene(after_cop[column].dropna(), before_cop[column].dropna())
        sig2 = label_p_value(p_l2)
        cop_levene.loc[i] = [round(stats_l2, 3), round(p_l2, 3), sig2]

        # 獨立兩樣本t test
        stat3, p3 = stats.ttest_ind(after_cop[column].dropna(), before_cop[column].dropna(), equal_var=True)
        significance3 = label_p_value(p3)
        cop.loc[i] = [round(stat3, 3), round(p3, 3), significance3]
        


    pollution_result.index = high_pollution.columns
    esg_score_result.index = high_pollution.columns
    esg_levene.index = high_pollution.columns
    cop_levene.index = high_pollution.columns
    cop.index = high_pollution.columns

    print('高污染or低污染產業', '\n', '--- 獨立兩樣本 Mann-whitney U test ---', '\n', pollution_result, '\n')
    print('ESG評分高低', '\n', '--- 同質變異數 Levene test ---', '\n', esg_levene, '\n')
    print('ESG評分高低', '\n', '--- 獨立兩樣本 t test ---','\n', esg_score_result, '\n')
    print('COP會議前後', '\n', '--- 同值變異數 Levene test ---', '\n', cop_levene, '\n')
    print('COP會議前後', '\n', '--- 獨立兩樣本 t test ---', '\n', cop)

if __name__ == '__main__':
    main()