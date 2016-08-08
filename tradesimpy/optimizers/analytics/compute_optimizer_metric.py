import optimizer_analytics
import exceptions as ex


def compute_optimizer_metric(metric_name, backtest_result, frequency):
    metric_name = metric_name.lower()

    if metric_name == 'sharpe_ratio':
        return optimizer_analytics.sharpe_ratio(backtest_result.log_returns, frequency)
    elif metric_name == 'sortino_ratio':
        return optimizer_analytics.sortino_ratio(backtest_result.log_returns, frequency)
    else:
        raise NotImplementedError("The optimizer metric %s is not supported." % metric)
