"""
Visualization utilities for search algorithm comparison results.

This module provides functions to generate charts and graphs for algorithm
performance analysis that can be used in both CLI and GUI interfaces.
"""

try:
    import matplotlib.pyplot as plt
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    np = None
    print("⚠️  matplotlib/numpy not available. Visualizations will be disabled.")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False
    sns = None
    print("⚠️  seaborn not available. Some visualizations will be disabled.")

from typing import Dict, Any, List
import os


class SearchVisualization:
    """
    Class for generating visualizations of search algorithm comparison results.
    """

    def __init__(self, save_dir: str = "results/charts"):
        """
        Initialize visualization generator.
        
        Args:
            save_dir: Directory to save chart files
        """
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("matplotlib is not available. Cannot create visualizations.")
        
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)
        
        # Set matplotlib style
        plt.style.use('default')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10

    def generate_performance_comparison_chart(self, results: Dict[str, Any], 
                                            save_file: str = "performance_comparison.png") -> str:
        """
        Generate performance metrics comparison bar chart.
        
        Args:
            results: Comparison results dictionary
            save_file: Filename to save the chart
            
        Returns:
            Path to saved chart file
        """
        aggregated = results['aggregated']
        algorithms = list(aggregated['algorithms'].keys())

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Metrics to compare
        metrics = ['map', 'mrr', 'f1@5', 'ndcg@10']
        x = np.arange(len(metrics))
        width = 0.35

        # Extract metric values
        algo1_metrics = [
            aggregated['algorithms'][algorithms[0]]['metrics'].get(m, 0) 
            for m in metrics
        ]
        algo2_metrics = [
            aggregated['algorithms'][algorithms[1]]['metrics'].get(m, 0) 
            for m in metrics
        ] if len(algorithms) > 1 else []
        
        # Create bars
        bars1 = ax.bar(x - width/2, algo1_metrics, width, 
                      label=algorithms[0], alpha=0.8, color='skyblue')
        if algo2_metrics:
            bars2 = ax.bar(x + width/2, algo2_metrics, width, 
                          label=algorithms[1], alpha=0.8, color='lightcoral')
        
        # Customize chart
        ax.set_xlabel('Metrics', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Algorithm Performance Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(['MAP', 'MRR', 'F1@5', 'NDCG@10'])
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 1.0)
        
        # Add value labels on bars
        for bars in [bars1, bars2] if len(algorithms) > 1 else [bars1]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{height:.3f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        
        # Save chart
        filepath = os.path.join(self.save_dir, save_file)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath

    def generate_precision_recall_chart(self, results: Dict[str, Any], 
                                      save_file: str = "precision_recall_trends.png") -> str:
        """
        Generate precision and recall trends vs K values chart.
        
        Args:
            results: Comparison results dictionary
            save_file: Filename to save the chart
            
        Returns:
            Path to saved chart file
        """
        aggregated = results['aggregated']
        algorithms = list(aggregated['algorithms'].keys())
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        k_values = [1, 3, 5, 10]
        colors = ['blue', 'red', 'green', 'orange']
        
        for i, algo_name in enumerate(algorithms):
            algo_data = aggregated['algorithms'][algo_name]
            metrics = algo_data['metrics']
            
            precisions = []
            recalls = []
            
            for k in k_values:
                precisions.append(metrics.get(f'precision@{k}', 0))
                recalls.append(metrics.get(f'recall@{k}', 0))
            
            # Plot precision
            ax.plot(k_values, precisions, marker='o', linewidth=2,
                   label=f'{algo_name} Precision', color=colors[i])
            # Plot recall
            ax.plot(k_values, recalls, marker='s', linestyle='--', linewidth=2,
                   label=f'{algo_name} Recall', color=colors[i], alpha=0.7)
        
        # Customize chart
        ax.set_xlabel('K Values', fontsize=12)
        ax.set_ylabel('Score', fontsize=12)
        ax.set_title('Precision & Recall vs K Values', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11, loc='best')
        ax.grid(True, alpha=0.3)
        max_precision = max(aggregated['algorithms'][algo]['metrics'].get('precision@10', 0) 
                           for algo in algorithms)
        max_recall = max(aggregated['algorithms'][algo]['metrics'].get('recall@10', 0) 
                        for algo in algorithms)
        max_value = max(max_precision, max_recall)
        ax.set_ylim(0, max_value * 1.1 if max_value > 0 else 0.1)
        
        plt.tight_layout()
        
        # Save chart
        filepath = os.path.join(self.save_dir, save_file)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath


    def generate_f1_score_trends_chart(self, results: Dict[str, Any], 
                                     save_file: str = "f1_score_trends.png") -> str:
        """
        Generate F1-Score trends vs K values chart.
        
        Args:
            results: Comparison results dictionary
            save_file: Filename to save the chart
            
        Returns:
            Path to saved chart file
        """
        aggregated = results['aggregated']
        algorithms = list(aggregated['algorithms'].keys())
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        k_values = [1, 3, 5, 10]
        colors = ['blue', 'red', 'green', 'orange']
        
        for i, algo_name in enumerate(algorithms):
            algo_data = aggregated['algorithms'][algo_name]
            metrics = algo_data['metrics']
            
            f1_scores = []
            for k in k_values:
                f1_scores.append(metrics.get(f'f1@{k}', 0))
            
            # Plot F1-scores
            ax.plot(k_values, f1_scores, marker='o', linewidth=3, markersize=8,
                   label=algo_name, color=colors[i])
        
        # Customize chart
        ax.set_xlabel('K Values', fontsize=12)
        ax.set_ylabel('F1-Score', fontsize=12)
        ax.set_title('F1-Score vs K Values', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        max_f1 = max(aggregated['algorithms'][algo]['metrics'].get('f1@10', 0) 
                    for algo in algorithms)
        ax.set_ylim(0, max_f1 * 1.1 if max_f1 > 0 else 0.1)
        
        plt.tight_layout()
        
        # Save chart
        filepath = os.path.join(self.save_dir, save_file)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return filepath

    def generate_all_charts(self, results: Dict[str, Any]) -> List[str]:
        """
        Generate all visualization charts.
        
        Args:
            results: Comparison results dictionary
            
        Returns:
            List of paths to saved chart files
        """
        chart_files = []
        
        print("📊 Generating visualization charts...")
        
        # Generate each chart
        chart_files.append(self.generate_performance_comparison_chart(results))
        print(f"  ✅ Performance comparison chart saved")
        
        chart_files.append(self.generate_precision_recall_chart(results))
        print(f"  ✅ Precision & Recall trends chart saved")
        
        chart_files.append(self.generate_f1_score_trends_chart(results))
        print(f"  ✅ F1-Score trends chart saved")
        
        print(f"📁 All charts saved to: {self.save_dir}")
        
        return chart_files

    def generate_summary_report(self, results: Dict[str, Any], 
                              chart_files: List[str]) -> str:
        """
        Generate a summary report with chart references.
        
        Args:
            results: Comparison results dictionary
            chart_files: List of chart file paths
            
        Returns:
            Summary report text
        """
        aggregated = results['aggregated']
        summary = results['summary']
        
        report = "🎨 VISUALIZATION SUMMARY REPORT\n"
        report += "=" * 50 + "\n\n"
        
        report += "📊 Generated Charts:\n"
        report += "-" * 20 + "\n"
        
        chart_names = [
            "Performance Metrics Comparison",
            "Precision & Recall Trends", 
            "F1-Score Trends"
        ]
        
        for i, (name, filepath) in enumerate(zip(chart_names, chart_files)):
            filename = os.path.basename(filepath)
            report += f"{i+1}. {name}: {filename}\n"
        
        report += f"\n📁 Charts saved to: {self.save_dir}\n\n"
        
        # Key insights
        report += "🎯 Key Visual Insights:\n"
        report += "-" * 25 + "\n"
        
        for insight in summary['key_insights']:
            report += f"• {insight}\n"
        
        report += f"\n📈 Best Performing Algorithms:\n"
        report += "-" * 30 + "\n"
        for metric, info in summary['best_algorithms'].items():
            report += f"• {metric.upper()}: {info['algorithm']} ({info['score']:.4f})\n"
        
        return report


def create_visualizations(results: Dict[str, Any], save_dir: str = "results/charts") -> List[str]:
    """
    Convenience function to create all visualizations.
    
    Args:
        results: Comparison results dictionary
        save_dir: Directory to save charts
        
    Returns:
        List of chart file paths
    """
    visualizer = SearchVisualization(save_dir)
    return visualizer.generate_all_charts(results)
