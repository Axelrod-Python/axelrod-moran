 
TF1

36,0.5700088731144631,0.19833076201142316,0.8571428571428571,0:C:0_C_7_C:0_D_1_C:1_C_11_D:1_D_11_D:2_C_8_D:2_D_8_C:3_C_3_C:3_D_12_D:4_C_6_C:4_D_3_C:5_C_11_C:5_D_8_D:6_C_13_D:6_D_14_C:7_C_4_D:7_D_2_D:8_C_14_D:8_D_8_D:9_C_0_C:9_D_10_D:10_C_8_C:10_D_15_C:11_C_6_D:11_D_5_D:12_C_6_D:12_D_9_D:13_C_9_D:13_D_8_D:14_C_8_D:14_D_13_D:15_C_4_C:15_D_5_C

Trained by VK with
python fsm_evolve.py --generations 1000 --states 16 --processes 16 --output "fsm_16_moran.csv" --objective moran --nmoran 12 --repetitions 10000

TF2

45,0.5496007098491571,0.2263723319050198,0.8571428571428571,0:C:0_C_13_D:0_D_12_D:1_C_3_D:1_D_4_D:2_C_14_D:2_D_9_D:3_C_0_C:3_D_1_D:4_C_1_D:4_D_2_D:5_C_12_C:5_D_6_C:6_C_1_C:6_D_14_D:7_C_12_D:7_D_2_D:8_C_7_D:8_D_9_D:9_C_8_D:9_D_0_D:10_C_2_C:10_D_15_C:11_C_7_D:11_D_13_D:12_C_3_C:12_D_8_D:13_C_7_C:13_D_10_D:14_C_10_D:14_D_7_D:15_C_15_C:15_D_11_D

Trained by MH with
python fsm_evolve.py --states 16 --objective moran --processes 2 --output fsm_moran_params.csv --nmoran 10 --repetitions 10000

TF3

39,0.6976042590949423,0.16477963655057146,0.9130434782608695,0:C:0_C_0_C:0_D_3_C:1_C_5_D:1_D_0_C:2_C_3_C:2_D_2_D:3_C_4_D:3_D_6_D:4_C_3_C:4_D_1_D:5_C_6_C:5_D_3_D:6_C_6_D:6_D_6_D:7_C_7_D:7_D_5_C

Trained by MH with
python fsm_evolve.py --generations 500 --states 8 --processes 4 --output "--fsm_moran_8.csv" --noise 0.01 --objective moran --nmoran 8
output file was renamed to fsm_moran_8_01n.csv

(default repetitions = 100)