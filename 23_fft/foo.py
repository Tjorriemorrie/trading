txt = ''.join(format(ord(x), 'b') for x in 'my foo is bar and baz')
print txt
from collections import Counter

secs = {
    '60': '111100',
    '30': '11110',
    '20': '10100',
    '12': '1100',
    '10': '1010',
    '6': '110',
    '5': '101',
    '3': '11',
    '2': '10',
    '1': '1',
    '0': '0',
}

for sz, bitr in secs.iteritems():
    cnt = 0
    for i in range(len(txt)):
        if txt[i:].startswith(bitr):
            cnt += 1
    print sz, str(cnt)



txt_bin = ''
bin1 = []
bin2 = []
bin3 = []
bin4 = []
bin5 = []
bin6 = []
bin7 = []
bin8 = []
with open('vid.mp4', 'rb') as f:
    for l in f:
        # print '{!r}'.format(l)
        # break
        for c in l:
            # print '{}'.format(c)
            c_b = ''.join(format(ord(b), '08b') for b in c)
            bin1.append(c_b[0])
            bin2.append(c_b[1])
            bin3.append(c_b[2])
            bin4.append(c_b[3])
            bin5.append(c_b[4])
            bin6.append(c_b[5])
            bin7.append(c_b[6])
            bin8.append(c_b[7])
            txt_bin += c_b
        if len(txt_bin) > 10000000:
            break

    # print txt_bin

bin1_counted = Counter(bin1)
bin2_counted = Counter(bin2)
bin3_counted = Counter(bin3)
bin4_counted = Counter(bin4)
bin5_counted = Counter(bin5)
bin6_counted = Counter(bin6)
bin7_counted = Counter(bin7)
bin8_counted = Counter(bin8)
print bin1_counted
print bin2_counted
print bin3_counted
print bin4_counted
print bin5_counted
print bin6_counted
print bin7_counted
