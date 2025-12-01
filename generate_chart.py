import matplotlib.pyplot as plt
import numpy as np

# Data from the paper's Table I
metrics = ['P@5', 'R@5', 'F1@5', 'NDCG@10', 'MAP']
keyword_scores = [0.62, 0.41, 0.49, 0.65, 0.52]
tfidf_scores = [0.74, 0.58, 0.65, 0.78, 0.68]

x = np.arange(len(metrics))
width = 0.35

fig, ax = plt.subplots(figsize=(10, 6))
rects1 = ax.bar(x - width/2, keyword_scores, width, label='Keyword Matching', color='#A9A9A9')
rects2 = ax.bar(x + width/2, tfidf_scores, width, label='TF-IDF', color='#2E8B57')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Score')
ax.set_title('Performance Comparison: Keyword Matching vs. TF-IDF')
ax.set_xticks(x)
ax.set_xticklabels(metrics)
ax.set_ylim(0, 1.0)
ax.legend()

# Add value labels
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

autolabel(rects1)
autolabel(rects2)

fig.tight_layout()

# Save the figure
plt.savefig('performance_comparison.png', dpi=300)
print("Chart generated: performance_comparison.png")

