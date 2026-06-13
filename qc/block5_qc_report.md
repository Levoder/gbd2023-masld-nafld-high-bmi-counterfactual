# Block 5 QC report
Generated: 2026-06-12T18:44:38
Overall: PASS

## Checks
# A tibble: 22 × 3
   check                                  status
   <chr>                                  <chr> 
 1 scenario_row_count                     PASS  
 2 component_row_count                    PASS  
 3 summary_2050_row_count                 PASS  
 4 model_status_row_count                 PASS  
 5 years_complete                         PASS  
 6 measures_complete                      PASS  
 7 scenarios_complete                     PASS  
 8 scenario_rates_non_negative            PASS  
 9 scenario_intervals_ordered             PASS  
10 scenario_a_not_above_observed_future   PASS  
11 scenario_b_not_above_scenario_a_future PASS  
12 reduction_fractions_in_unit_interval   PASS  
13 model_status_documents_rounded_counts  PASS  
14 population_projection_future_complete  PASS  
15 population_projection_positive         PASS  
16 future_population_method_is_wpp        PASS  
17 population_2050_matches_wpp_reference  PASS  
18 wpp_age_review_complete                PASS  
19 figure4_png_exists_nonempty            PASS  
20 figure4_svg_exists_nonempty            PASS  
21 figure4_pdf_exists_nonempty            PASS  
22 figure4_tiff_exists_nonempty           PASS  
   detail                                                                       
   <chr>                                                                        
 1 "366 vs 366"                                                                 
 2 "244 vs 244"                                                                 
 3 "6 vs 6"                                                                     
 4 "4 vs 4"                                                                     
 5 "1990-2050"                                                                  
 6 "1,2"                                                                        
 7 "Observed projection; Scenario A: sex-equalized high BMI; Scenario B: high B…
 8 "0"                                                                          
 9 "0"                                                                          
10 "0"                                                                          
11 "0"                                                                          
12 "0.120691633177998,0.113246521479422"                                        
13 "bapc_rounded_counts_after_fractional_error: The inla program call crashed.\…
14 "432"                                                                        
15 "149774.602460709"                                                           
16 "UN WPP 2024 PopulationExposureByAge5GroupSex_Medium, medium variant, 34 mat…
17 "1744298695 vs 1744298695"                                                   
18 "448"                                                                        
19 "bytes= 174657"                                                              
20 "bytes= 27524"                                                               
21 "bytes= 39180"                                                               
22 "bytes= 340606"                                                              

## 2050 summary
# A tibble: 6 × 10
  measure_id measure_name                          
       <dbl> <chr>                                 
1          1 Deaths                                
2          1 Deaths                                
3          1 Deaths                                
4          2 DALYs (Disability-Adjusted Life Years)
5          2 DALYs (Disability-Adjusted Life Years)
6          2 DALYs (Disability-Adjusted Life Years)
  scenario                            year rate_mean rate_lower rate_upper
  <chr>                              <dbl>     <dbl>      <dbl>      <dbl>
1 Observed projection                 2050      1.45          0       4.82
2 Scenario A: sex-equalized high BMI  2050      1.44          0       4.82
3 Scenario B: high BMI at TMREL       2050      1.34          0       4.82
4 Observed projection                 2050     47.1           0     130.  
5 Scenario A: sex-equalized high BMI  2050     46.2           0     130.  
6 Scenario B: high BMI at TMREL       2050     39.3           0     130.  
  absolute_reduction_vs_observed percent_reduction_vs_observed
                           <dbl>                         <dbl>
1                         0                              0    
2                         0.0143                         0.982
3                         0.118                          8.14 
4                         0                              0    
5                         0.885                          1.88 
6                         7.82                          16.6  
  reduction_fraction
               <dbl>
1              0    
2              0.121
3              1    
4              0    
5              0.113
6              1    

## Outputs
- QC checks: `./tables/block5_qc_checks.csv`
- QC 2050 summary: `./tables/block5_qc_2050_summary.csv`
- Report: `./logs/block5_qc_report.md`
