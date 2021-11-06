# Notes About Missing Data

## Corrupted data files

Perfect lines in the CTD data files have a hash-mark `#` that separates the server info (time and IP) from the data.
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
2013-04-10T02:30:44Z,166.241.175.135,#
2018-08-11T16:16:05Z,166.148.81.45,# 20.8012,  4.69123,    3.104, 0.3951, 0.0000, 0.0001, 0.0003,  33.5350, 11 Aug 201ø 16:16:00,  23.4325, 13.9, 200.1
```

Also, times can be missing or out of order.

### The solution

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


### Converting to float
 
To convert temperature to a float, the `#` must be removed. Originally, I use this:
```      
data[start_column] = data[start_column].str.replace('#', '')
```
but then a Stearn's Wharf file showed up with Issue #3. Instead, I had to brutally restrict to just digits:
```
data[start_column].replace(regex=True, inplace=True, to_replace=r'[^0-9.\-]', value=r'')
```


## Undocumented change in time format

The date/time format of these data changes in the middle of the file!

```
2016-03-03T00:07:40Z,172.16.117.233,time out
2016-03-03T00:08:12Z,166.241.139.252,# 18.4374,  4.44665,    3.088, 0.0010, 0.0060, 0.0556, 0.0103,  33.4196, 03 Mar 2016, 00:09:25,  23.9544, 11.8, 597.7
2016-03-03T00:10:11Z,166.241.139.252,# 18.4341,  4.44690,    3.062, 0.0008, 0.0068, 0.0570, 0.0104,  33.4244, 03 Mar 2016, 00:11:25,  23.9589, 11.8, 507.7
2016-03-03T00:10:55Z,166.148.81.45,# 17.2690,  4.33962,    2.854, 4.7664, 0.0012, 0.0002, 0.0003,  33.4671, 03 Mar 2016 00:10:40,  24.2744, 14.1, 135.2
2016-03-03T00:11:20Z,172.16.117.233,# 17.9473,  4.41324,    3.584, 0.0002, 0.0002, 0.2938, 0.0001,  33.5375, 03 Mar 2016 00:11:13,  24.1650, 11.9, 171.0
2016-03-03T00:11:20Z,172.16.117.233,error --> alarm time not far enough in the future, resetting alarm to 5 sec from now
2016-03-03T00:11:21Z,172.16.117.233,SBE 16plus
```

Before: date and time are in different columns separated by a comma. After: they are in the same column, 
separated by a space. It takes ~15 minutes at the beginning of this file for all instruments to switch over.

Having the number of columns change makes it hard to parse the data, so that whole day is dropped. Also,
the changing number of columns requires separate instrument_sets for files before and after.

Then, or course, there is [SIO 10/19/2015](https://sccoos.org/dr/data/data/2015-10/data-20151019.dat) that has
a single line of space separated date and time in a file from before the transition. To avoid having another 
special case, that line is dropped too.


## Data from separate sites in the same files

For the first few years, data from all deployed instruments were written to the same file. That file
was in the subdirectory `data/` (what we started calling`scripps_pier`). Different sites are identified 
by their IP addresses.

Here's an example:
```
2013-11-15T00:02:00Z,166.241.139.252,# 18.3637,  4.45391,    2.645, 0.3939, 0.0002, 0.1783, 0.0001,  33.5409, 15 Nov 2013, 00:01:29,  24.0654, 12.6, 172.9
2013-11-15T00:02:07Z,166.148.81.45,# 16.7047,  4.29693,    2.474, 0.0003, 0.0006, 0.0682, 0.0000,  33.5668, 15 Nov 2013, 00:02:03,  24.4835, 14.0, 191.6
2013-11-15T00:02:32Z,166.241.175.135,# 17.8930,  4.39277,    2.395, 0.0001, 0.0001, 4.9288, 0.0001,  33.4083, 15 Nov 2013, 00:02:06,  24.0795, 12.5, 210.1
2013-11-15T00:05:59Z,166.241.139.252,# 18.2029,  4.43817,    2.649, 0.3824, 0.0001, 0.1741, 0.0001,  33.5395, 15 Nov 2013, 00:05:29,  24.1041, 12.6, 168.6
2013-11-15T00:06:07Z,166.148.81.45,# 16.7012,  4.29662,    2.503, 0.0001, 0.0005, 0.0660, 0.0000,  33.5671, 15 Nov 2013, 00:06:03,  24.4846, 14.0, 190.1
```

One by one, the sites were transferred to their own subdirectories:
* Newport Pier on 2016-20-11 into `newport_pier/` (after a gap of a few hours)
* Stearns Wharf on 2018-02-26 into `stearns_wharf/` (after a gap of several days)
* Santa Monica on 2018-10-03 into `santa_monica_pier/` (after a gap of several years)

Luckily, once this transfer happens, that IP never appears in the `scripps_pier/` files again, so before and after this
transition can be described by separate instrument_sets.

However, during Newport's transition, data from the same instrument is written into both 
`scripps_pier/2016-03/data_20162011.dat` and  `newport_pier/2016-10/data-20161011.dat`. Since this code works 
with entire files, I have to choose which file to process (it can'tdo both and merge the results). I did that 
by setting the start of the new instrument_set to the next day (10/12/2016)


## The IP address changes for a single site

For those early years, this code identifies data from a site by the IP address. This address changed for 2 sites:

* Newport Pier from 166.241.139.252 to 166.140.102.113 (after a gap of a few months)
* Scripps Pier from 132.239.117.226 to 172.16.117.233 (after a gap of ~1 day)

These changes don't result in missing data.  Just thought I'd mention it.
