import matplotlib.pyplot as plt
import pandas as pd

eval_all = pd.read_csv('time.csv')
print(eval_all)
# plot All
plt.plot(eval_all['N'], eval_all['time'], marker='o', markersize=5, color="blue", label="all-to-all")

plt.title("Transfer Speed Evaluation")
plt.xlabel("Number of peers holding files")
plt.ylabel("Total Respond time(sec)")

plt.savefig("eval.png")
plt.show()