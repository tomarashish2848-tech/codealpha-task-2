## 1. Raw data

- Shape: (1018, 7)
- Missing values per column:
```
Region                                      0
Date                                        0
Frequency                                   0
Estimated Unemployment Rate (%)            30
Estimated Employed                         25
Estimated Labour Participation Rate (%)    15
Zone                                        0
```

## 2. Cleaning log

- Duplicate rows removed: 10
- Region names / Frequency labels trimmed and standardised; mixed date formats unified
- Impossible unemployment values (<0 or >100) set to missing: 13
- Total missing cells (incl. the above) imputed by per-state linear interpolation: 83
- Clean shape: (1008, 10) | regions: 28 | Jan 2019 to Dec 2021

## 3. Descriptive statistics

```
       Unemployment Rate     Employed  Labour Participation Rate
count            1008.00      1008.00                    1008.00
mean                8.17  23713462.52                      44.77
std                 5.76  13442779.79                       5.67
min                 0.80   5021410.00                      33.67
25%                 4.18  11725890.00                      40.35
50%                 6.48  21146327.00                      43.34
75%                11.01  32087180.75                      48.18
max                40.18  57025361.00                      62.98
```

- Average national unemployment pre-COVID (Jan 2019–Feb 2020): **7.22%**
- National peak: **20.45% in April 2020** (2.8x pre-COVID)
- Second-wave peak: **11.48% in May 2021**
- Employed (sum across states): 674M in Jan 2019 -> low of 534M in Apr 2020
- First month back within 10% of the pre-COVID average after the peak: **July 2020**

**Mean unemployment by period (average of states)**
```
                          mean    max
Period                               
1 Pre-COVID               7.22   7.52
2 First wave / lockdown  15.00  20.45
3 Recovery                6.98   8.05
4 Second wave             9.24  11.48
5 Post second wave        6.66   7.28
```

## 4. State-level COVID impact (first wave)

**Largest percentage-point increase**
```
                   pre  peak  increase_pp  multiple
Region                                             
Delhi             13.4  36.5         23.1       2.7
Haryana           18.1  40.2         22.1       2.2
Himachal Pradesh  12.1  32.9         20.8       2.7
Bihar              9.8  30.2         20.5       3.1
Rajasthan         11.4  31.5         20.1       2.8
Tripura           15.7  34.7         19.0       2.2
Jharkhand          9.1  28.0         18.9       3.1
Kerala             8.3  26.8         18.5       3.2
```
**Smallest percentage-point increase**
```
            pre  peak  increase_pp  multiple
Region                                      
Meghalaya   2.5   5.1          2.6       2.0
Odisha      3.4   9.2          5.8       2.7
Puducherry  1.7   8.6          7.0       5.1
Tamil Nadu  1.3   8.4          7.1       6.7
Sikkim      4.2  11.8          7.6       2.8
```

**Zones (average of member states: pre-COVID mean vs lockdown peak)**
```
             pre  peak  multiple
Zone                            
Central      4.8  14.3       3.0
East         6.9  21.2       3.1
North       10.9  28.5       2.6
North-East   6.8  16.1       2.4
South        4.0  14.1       3.5
West         5.3  18.0       3.4
```

## 5. Seasonality (pre-COVID, 2019 only + Jan-Feb 2020)

- Highest month: May (+4.5%), lowest: Jan (-3.2%)
- Caveat: only ~14 pre-COVID months exist, so seasonal estimates are indicative, not definitive.

- Correlation (national series) between unemployment and labour participation: -0.97

## 6. Recovery speed

- Median months from peak to within 20% of own pre-COVID level: 3
- States that never got back within 20% in the data window: 0

- Mean state-month rate: pre-COVID 7.22% vs lockdown period 15.00% (Welch t = 8.6, p < 0.001)