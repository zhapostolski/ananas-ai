# ── SNS topic for alerts ──────────────────────────────────────────────────────

resource "aws_sns_topic" "alerts" {
  name = "ananas-ai-alerts"
}

resource "aws_sns_topic_subscription" "email" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# ── CloudWatch alarms ─────────────────────────────────────────────────────────

resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "ananas-ai-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/EC2"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "EC2 CPU above 80% for 10 minutes"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]

  dimensions = { InstanceId = aws_instance.runtime.id }
}

resource "aws_cloudwatch_metric_alarm" "instance_status" {
  alarm_name          = "ananas-ai-instance-status"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "StatusCheckFailed"
  namespace           = "AWS/EC2"
  period              = 60
  statistic           = "Maximum"
  threshold           = 0
  alarm_description   = "EC2 status check failed"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = { InstanceId = aws_instance.runtime.id }
}

resource "aws_cloudwatch_metric_alarm" "disk_usage" {
  alarm_name          = "ananas-ai-disk-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "disk_used_percent"
  namespace           = "CWAgent"
  period              = 300
  statistic           = "Average"
  threshold           = 85
  alarm_description   = "Disk usage above 85%"
  alarm_actions       = [aws_sns_topic.alerts.arn]

  dimensions = {
    InstanceId = aws_instance.runtime.id
    path       = "/"
    fstype     = "ext4"
    device     = "nvme0n1p1"
  }
}

# ── Dead-man heartbeat alarm ──────────────────────────────────────────────────
# Fires if run-brief hasn't published a heartbeat in 25 hours (1 missed run = alert).
# The metric is published by ananas_ai.cli._publish_heartbeat() after every
# successful run-brief completion.

resource "aws_cloudwatch_metric_alarm" "brief_missing" {
  alarm_name          = "ananas-ai-brief-missing"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "BriefHeartbeat"
  namespace           = "AnanasAI"
  period              = 90000 # 25 hours in seconds
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "breaching"
  alarm_description   = "Daily marketing brief did not run in the last 25 hours"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  ok_actions          = [aws_sns_topic.alerts.arn]
}

# ── CloudWatch Log Group for agent logs ───────────────────────────────────────

resource "aws_cloudwatch_log_group" "agents" {
  name              = "/ananas-ai/agents"
  retention_in_days = 30
}

resource "aws_cloudwatch_log_group" "system" {
  name              = "/ananas-ai/system"
  retention_in_days = 14
}

# ── CloudWatch dashboard ──────────────────────────────────────────────────────

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "ananas-ai-runtime"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          title   = "EC2 CPU"
          region  = var.aws_region
          metrics = [["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.runtime.id]]
          period  = 300
          stat    = "Average"
          view    = "timeSeries"
        }
      },
      {
        type = "metric"
        properties = {
          title   = "EC2 Network"
          region  = var.aws_region
          metrics = [
            ["AWS/EC2", "NetworkIn",  "InstanceId", aws_instance.runtime.id],
            ["AWS/EC2", "NetworkOut", "InstanceId", aws_instance.runtime.id],
          ]
          period = 300
          stat   = "Sum"
          view   = "timeSeries"
        }
      },
      {
        type = "metric"
        properties = {
          title   = "Daily Brief Heartbeat"
          region  = var.aws_region
          metrics = [["AnanasAI", "BriefHeartbeat"]]
          period  = 86400
          stat    = "Sum"
          view    = "timeSeries"
          annotations = {
            horizontal = [{ value = 1, label = "Expected", color = "#2ca02c" }]
          }
        }
      },
    ]
  })
}
