# Notes about Corrupted Data Files

## The problem

Perfect lines in these data files have a hash-mark `#` that separates the server info (time and IP) from the data.
A good line will look like:

```
2021-10-10T02:38:20Z,166.148.81.45,# 17.8714,  4.39094,    1.813, 0.2454, 0.0000, 0.0001, 0.0001,  33.4107, 10 Oct 2021 02:38:13,  24.0865, 13.7, 192.6
```

There are a million ways this perfection can be corrupted. Here are a few ...

``` 
2021-10-10T02:14:20Z,166.148.81.45,,    1.918, 0.3063, 0.0000, 0.0002, 0.0001,  33.4141, 10 Oct 2021 02:14:13,  24.0774, 13.8, 192.2
2021-10-10T02:18:20Z,166.148.81.45,��iʢ��b�rª�b�r�ʚ�b�r����b�r����b�r����b��r����b��z�с2021 02:18:13,  24.0801, 13.8, 192.6
2021-10-10T02:23:20Z,0.0.0.0,#
2021-10-10T22:58:20Z,166.148.81.45,�# 18.2001,  4.42358,    2.926, 0.2752, 0.0000, 0.0001, 0.0002,  33.4184, 10 Oct 2021 22:58:13,  24.0121, 13.8, 189.3
2021-10-10T23:02:20Z,166.148.81.45, 18.3912,  4.44245,    2.924, 0.2435, 0.0000, 0.0002, 0.0001,  33.4219, 10 Oct 2021 23:02:13,  23.9676, 13.8, 189.9
2021-02-26T19:49:20Z,166.140.102.113,�#�L�邢�b�r�ʢ��b�r���b�r����b��r���b�r������b��r����b��2���2021 19:49:12,  24.8468, 12.6, 215.7
2021-02-27T09:17:20Z,166.140.102.113,�#�.��927,  4.12167,    2.557, 0.0000, 17.345, 0.754782,  33.4586, 27 Feb 2021 09:17:12,  24.7854, 12.6, 220.5
```

Also, times can be missing or out of order.

## The solution

The wide variation in contaminated lines means that it is hard to parse the good from the bad.  For instance,
some lines look OK except that they are just missing the `#`. But other lines are total goners. There
are even lines where gibberish is inserted into what looks like OK data.

Even worse, I can't be sure I've seen every bad permutation possible.

So I had to make some choices and assumptions:
0. Avoid ingesting bad data even at the risks of losing a few points.
1. If the IP is obviously bad, the data is also bad: remove the line.
2. If there is any gibberish at all, remove the line,
3. If there is no `#`, the beginning of the data cannot be determined: remove the line
4. Sort data by time before merge with calibration coefficients.


Caveats

* In bad line 5 above, it looks like good data without `#`. Should I try and save that line?  No.
  * What if a digit was also dropped in addition to `#`?  In that (so far hypothetical) case, 5.0345 might look right, but it's really supposed to be 15.0345.    
* In some cases, it looks like some fields might be OK. 
  * Oh, but which ones?
* For awhile, if there was a gibberish character in the temperature field (bad line 4 above) I would try
 and filter to just digits in order to keep the line.
  * But then I came across lines 6 and 7 in newport_pier data with `#` and gibberish mixed together
  * If line 7 is saved then the temperature data is corrupted.
  * Just remove any line with gibberish = simple solution.
* Some of the tests might not be needed, but I'm paranoid something will slip through.


## Converting to float
 
To convert temperature to a float, the `#` must be removed. Originally, I use this:
```      
data[start_column] = data[start_column].str.replace('#', '')
```
but then a Stearn's Whard file showed up with Issue #3. Instead, I had to brutally restrict to just digits:
```
data[start_column].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]', value=r'')
```


## Undocumented change in instrument set

There's a file for SIO where the date/time format changes in the middle of a file!

```
2016-03-03T00:07:40Z,172.16.117.233,time out
2016-03-03T00:08:12Z,166.241.139.252,# 18.4374,  4.44665,    3.088, 0.0010, 0.0060, 0.0556, 0.0103,  33.4196, 03 Mar 2016, 00:09:25,  23.9544, 11.8, 597.7
2016-03-03T00:10:11Z,166.241.139.252,# 18.4341,  4.44690,    3.062, 0.0008, 0.0068, 0.0570, 0.0104,  33.4244, 03 Mar 2016, 00:11:25,  23.9589, 11.8, 507.7
2016-03-03T00:10:55Z,166.148.81.45,# 17.2690,  4.33962,    2.854, 4.7664, 0.0012, 0.0002, 0.0003,  33.4671, 03 Mar 2016 00:10:40,  24.2744, 14.1, 135.2
2016-03-03T00:11:20Z,172.16.117.233,# 17.9473,  4.41324,    3.584, 0.0002, 0.0002, 0.2938, 0.0001,  33.5375, 03 Mar 2016 00:11:13,  24.1650, 11.9, 171.0
2016-03-03T00:11:20Z,172.16.117.233,error --> alarm time not far enough in the future, resetting alarm to 5 sec from now
2016-03-03T00:11:21Z,172.16.117.233,SBE 16plus
```

Prior: date and time are in separate columns, and afterwards, they are in the same column. 
(Also there are lots of junky lines but without gibberish)

Having the number of columns change is unacceptable, so drop that day. Otherwise, need 2 different instrument 
sets for SIO to adjust to that.

Then, or course, there is [SIO 10/19/2015](https://sccoos.org/dr/data/data/2015-10/data-20151019.dat) that has
a single line of the single file in a file full of date, time.  So need a special catch for that too.


## Data from 2 different servers

From SIO again:

```
2015-10-19T00:00:15Z,166.241.139.252,# 22.0211,  4.64235,    2.919, 0.0000, 0.0000, 0.1106, 0.0010,  32.2161, 19 Oct 2015, 00:00:52,  22.0982, 12.3, 242.0
2015-10-19T00:02:15Z,166.241.139.252,# 22.0417,  4.64570,    2.895, 0.0000, 0.0000, 0.1149, 0.0002,  32.2269, 19 Oct 2015, 00:02:52,  22.1007, 12.4, 213.0
2015-10-19T00:02:51Z,172.16.117.233,# 22.5955,  4.83420,    3.384, 0.0000, 0.0000, 5.0000, 0.0014,  33.2691, 19 Oct 2015, 00:01:56,  22.7363, 11.8, 228.3
2015-10-19T00:02:52Z,172.16.117.233,SeacatPlus
2015-10-19T00:03:52Z,0.0.0.0,S>
2015-10-19T00:04:15Z,166.241.139.252,# 22.0591,  4.64740,    2.903, 0.0000, 0.0000, 0.1202, 0.0002,  32.2271, 19 Oct 2015, 00:04:52,  22.0961, 12.3, 223.8
2015-10-19T00:06:16Z,166.241.139.252,# 22.0783,  4.64930,    2.906, 0.0000, 0.0000, 0.1232, 0.0000,  32.2276, 19 Oct 2015, 00:06:52,  22.0911, 12.3, 233.5
2015-10-19T00:08:15Z,166.241.139.252,# 22.0894,  4.65019,    2.877, 0.0000, 0.0000, 0.1244, 0.0002,  32.2263, 19 Oct 2015, 00:08:52,  22.0870, 12.3, 254.5
2015-10-19T00:08:52Z,172.16.117.233,# 22.6756,  4.84232,    3.285, 0.0000, 0.0000, 5.0000, 0.0013,  33.2708, 19 Oct 2015, 00:07:57,  22.7150, 11.8, 194.8
2015-10-19T00:08:53Z,172.16.117.233,SeacatPlus
2015-10-19T00:09:53Z,0.0.0.0,S>

```

Only lines from server 172.16.117.233 are in [the ERDDAP server](https://erddap.sccoos.org/erddap/tabledap/autoss.htmlTable?station%2Ctime%2Ctemperature&station=%22scripps_pier%22&time%3E=2015-10-19T00%3A00%3A00Z&time%3C=2015-10-19T23%3A59%3A00Z)