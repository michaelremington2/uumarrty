import csv 

data = []
row = []

for i in range(0,10):
    k_id = 'krat_{}'.format(i)
    val1 = i+1
    val2 = i+2
    row.append(k_id)
    row.append(val1)
    row.append(val2)
    data.append(row)
    row = []


# with open('output.tsv', 'w', newline='') as f_output:
#     tsv_output = csv.writer(f_output, delimiter='\t')
#     tsv_output.writerow(data)

output_fp = list('ecosystem_sim')

fp = output_fp[-1]
print(fp)