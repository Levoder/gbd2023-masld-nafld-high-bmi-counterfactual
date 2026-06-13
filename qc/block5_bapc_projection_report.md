# Block 5 BAPC projection report
Generated: 2026-06-12T18:44:25

## Quality reminders
- Q23: Rscript is not on PATH; this run used the discovered R 4.5.2 executable. INLA and BAPC were installed and loaded.
- Q24: Future person-years were replaced with UN WPP 2024 PopulationExposureByAge5GroupSex_Medium, medium variant, summed across the 34 matched study locations.
- Q25: BAPC intervals are model-projection intervals from GBD point estimates; they do not include draw-level GBD uncertainty, RR-PSA, or lean-MASLD sensitivity.
- Q26: Scenario A and B are nested deterministic counterfactual layers and must not be added.
- Q27: INLA did not fit fractional GBD expected counts stably; this run documents the failure and uses rounded counts for the BAPC likelihood, with non-negative truncation of rate lower bounds.

## Model status
# A tibble: 4 × 6
  measure_id measure_name                           burden_type  
       <dbl> <chr>                                  <chr>        
1          1 Deaths                                 total        
2          1 Deaths                                 high_bmi_attr
3          2 DALYs (Disability-Adjusted Life Years) total        
4          2 DALYs (Disability-Adjusted Life Years) high_bmi_attr
  model_status                                                                  
  <chr>                                                                         
1 "bapc_rounded_counts_after_fractional_error: The inla program call crashed.\n…
2 "bapc_rounded_counts_after_fractional_error: The inla program call crashed.\n…
3 "bapc_rounded_counts_after_fractional_error: The inla program call crashed.\n…
4 "bapc_rounded_counts_after_fractional_error: The inla program call crashed.\n…
  min_rate max_rate
     <dbl>    <dbl>
1   1.45      2.06 
2   0.0256    0.118
3  42.3      55.6  
4   0.741     7.82 

## Scenario definitions
- Observed projection: BAPC projection of total MASLD-related burden.
- Scenario A: observed total projection minus the 2019-2023 mean sex-equalization avoidable fraction of the projected high-BMI-attributable component.
- Scenario B: observed total projection minus the full projected high-BMI-attributable component, interpreted as the TMREL theoretical upper bound.

## Reduction fractions
# A tibble: 2 × 7
  measure_id measure_name                           years_used avoidable_sum
       <dbl> <chr>                                  <chr>              <dbl>
1          1 Deaths                                 2019-2023           458.
2          2 DALYs (Disability-Adjusted Life Years) 2019-2023         12130.
  high_bmi_attr_sum scenario_a_reduction_fraction scenario_b_reduction_fraction
              <dbl>                         <dbl>                         <dbl>
1             3794.                         0.121                             1
2           107111.                         0.113                             1

## WPP population exposure coverage
# A tibble: 28 × 3
    Time matched_locations expected_locations
   <dbl>             <int>              <int>
 1  2023                34                 34
 2  2024                34                 34
 3  2025                34                 34
 4  2026                34                 34
 5  2027                34                 34
 6  2028                34                 34
 7  2029                34                 34
 8  2030                34                 34
 9  2031                34                 34
10  2032                34                 34
11  2033                34                 34
12  2034                34                 34
13  2035                34                 34
14  2036                34                 34
15  2037                34                 34
16  2038                34                 34
17  2039                34                 34
18  2040                34                 34
19  2041                34                 34
20  2042                34                 34
21  2043                34                 34
22  2044                34                 34
23  2045                34                 34
24  2046                34                 34
25  2047                34                 34
26  2048                34                 34
27  2049                34                 34
28  2050                34                 34

## Population totals
# A tibble: 3 × 3
   year
  <dbl>
1  2023
2  2024
3  2050
  population_projection_method                                                  
  <chr>                                                                         
1 observed proxy from D_total Number/Rate                                       
2 UN WPP 2024 PopulationExposureByAge5GroupSex_Medium, medium variant, 34 match…
3 UN WPP 2024 PopulationExposureByAge5GroupSex_Medium, medium variant, 34 match…
   population
        <dbl>
1 1629974769.
2 1641688146 
3 1744298695 

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
  <fct>                              <int>     <dbl>      <dbl>      <dbl>
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
- BAPC input: `./tables/block5_bapc_input_age_year.csv`
- Population projection/person-years: `./tables/block5_population_proxy_projection.csv`
- WPP age review: `./tables/block5_wpp_population_exposure_age_review.csv`
- WPP coverage: `./tables/block5_wpp_population_exposure_coverage.csv`
- Component rates: `./tables/block5_bapc_projected_rates_components.csv`
- Scenario rates: `./tables/block5_projection_scenarios.csv`
- 2050 summary: `./tables/block5_2050_summary.csv`
- Figure 4: `./figures/block5_fig4_bapc_projection_scenarios.png`
- Report: `./logs/block5_bapc_projection_report.md`
