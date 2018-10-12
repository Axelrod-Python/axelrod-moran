# Script to rename all images files produced from running main.ipynb and the
# tikz images.
convert -density 900 -quality 1000 moran_process.pdf Fig1.eps
convert -density 900 -quality 1000 tf1.pdf Fig2.eps
convert -density 900 -quality 1000 tf2.pdf Fig3.eps
convert -density 900 -quality 1000 tf3.pdf Fig4.eps
cp Alternator_v_WSLS.eps Fig5.eps
cp Calculator_v_Arrogant_QLearner.eps Fig6.eps
cp average_rank_vs_population_size_invade.eps Fig7.eps
cp average_rank_vs_population_size_resist.eps Fig8.eps
cp average_rank_vs_population_size_coexist.eps Fig9.eps
cp correlation_heatmaps.eps Fig10.eps
cp cooperation_heatmap.eps Fig11.eps
cp boxplot_3_invade.eps S1_Fig.eps
cp boxplot_4_invade.eps S2_Fig.eps
cp boxplot_5_invade.eps S3_Fig.eps
cp boxplot_6_invade.eps S4_Fig.eps
cp boxplot_7_invade.eps S5_Fig.eps
cp boxplot_8_invade.eps S6_Fig.eps
cp boxplot_9_invade.eps S7_Fig.eps
cp boxplot_10_invade.eps S8_Fig.eps
cp boxplot_11_invade.eps S9_Fig.eps
cp boxplot_12_invade.eps S10_Fig.eps
cp boxplot_13_invade.eps S11_Fig.eps
cp boxplot_14_invade.eps S12_Fig.eps
cp boxplot_3_resist.eps S13_Fig.eps
cp boxplot_4_resist.eps S14_Fig.eps
cp boxplot_5_resist.eps S15_Fig.eps
cp boxplot_6_resist.eps S16_Fig.eps
cp boxplot_7_resist.eps S17_Fig.eps
cp boxplot_8_resist.eps S18_Fig.eps
cp boxplot_9_resist.eps S19_Fig.eps
cp boxplot_10_resist.eps S20_Fig.eps
cp boxplot_11_resist.eps S21_Fig.eps
cp boxplot_12_resist.eps S22_Fig.eps
cp boxplot_13_resist.eps S23_Fig.eps
cp boxplot_14_resist.eps S24_Fig.eps
