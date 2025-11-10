"""
Email service using Resend
Handles all email notifications for the PMS
"""

import os
from typing import List, Optional
import resend

# Configure Resend
resend.api_key = "re_b5tqpN9T_6PCcJKM3cWwP4EDAFsv2rZhy"
FROM_EMAIL = "vem@spryntr.co"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

class EmailService:
    """Email service for sending notifications"""

    @staticmethod
    def send_email(
        to: List[str],
        subject: str,
        html: str,
        reply_to: Optional[str] = None
    ):
        """Send email using Resend"""
        try:
            params = {
                "from": FROM_EMAIL,
                "to": to,
                "subject": subject,
                "html": html,
            }

            if reply_to:
                params["reply_to"] = reply_to

            response = resend.Emails.send(params)
            return response
        except Exception as e:
            print(f"Error sending email: {e}")
            raise

    @staticmethod
    def send_onboarding_email(user_email: str, user_name: str, onboarding_token: str):
        """Send onboarding email with password setup link"""
        onboarding_link = f"{FRONTEND_URL}/onboard?token={onboarding_token}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #3b82f6;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 500;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 8px 8px;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .code {{
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 6px;
                    font-family: monospace;
                    margin: 15px 0;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Welcome to Nigcomsat PMS</h1>
            </div>
            <div class="content">
                <p>Hello {user_name},</p>
                <p>Your account has been created in the Nigcomsat Performance Management System. To complete your registration and set up your password, please click the button below:</p>
                <center>
                    <a href="{onboarding_link}" class="button">Set Up Your Password</a>
                </center>
                <p>Or copy and paste this link in your browser:</p>
                <div class="code">{onboarding_link}</div>
                <p><strong>Important:</strong> This link is valid for one-time use only. Once you set your password, you'll be able to log in to your account.</p>
                <p>If you didn't expect this email, please contact your system administrator.</p>
            </div>
            <div class="footer">
                <p>This is an automated message from Nigcomsat Performance Management System</p>
                <p>&copy; 2024 Nigcomsat. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(
            to=[user_email],
            subject="Welcome to Nigcomsat PMS - Set Up Your Password",
            html=html
        )

    @staticmethod
    def send_password_reset_email(user_email: str, user_name: str, reset_token: str):
        """Send password reset email"""
        reset_link = f"{FRONTEND_URL}/reset-password?token={reset_token}"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #ef4444;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 500;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 8px 8px;
                    color: #6b7280;
                    font-size: 14px;
                }}
                .code {{
                    background: #f3f4f6;
                    padding: 15px;
                    border-radius: 6px;
                    font-family: monospace;
                    margin: 15px 0;
                    word-break: break-all;
                }}
                .warning {{
                    background: #fef3c7;
                    border-left: 4px solid #f59e0b;
                    padding: 15px;
                    margin: 15px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello {user_name},</p>
                <p>We received a request to reset your password for your Nigcomsat PMS account. Click the button below to reset your password:</p>
                <center>
                    <a href="{reset_link}" class="button">Reset Your Password</a>
                </center>
                <p>Or copy and paste this link in your browser:</p>
                <div class="code">{reset_link}</div>
                <div class="warning">
                    <strong>Security Notice:</strong>
                    <ul style="margin: 10px 0;">
                        <li>This link is valid for one-time use only</li>
                        <li>If you didn't request this reset, please ignore this email</li>
                        <li>Your password will remain unchanged unless you use this link</li>
                    </ul>
                </div>
                <p>If you have any concerns, please contact your system administrator immediately.</p>
            </div>
            <div class="footer">
                <p>This is an automated message from Nigcomsat Performance Management System</p>
                <p>&copy; 2024 Nigcomsat. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(
            to=[user_email],
            subject="Reset Your Nigcomsat PMS Password",
            html=html
        )

    @staticmethod
    def send_task_assignment_email(user_email: str, user_name: str, task_title: str, task_id: str, due_date: str, created_by_name: str):
        """Send task assignment notification"""
        task_link = f"{FRONTEND_URL}/dashboard/tasks"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .task-card {{
                    background: #f9fafb;
                    border-left: 4px solid #3b82f6;
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 6px;
                }}
                .task-card h3 {{
                    margin-top: 0;
                    color: #1f2937;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #3b82f6;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 500;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 8px 8px;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>New Task Assigned</h1>
            </div>
            <div class="content">
                <p>Hello {user_name},</p>
                <p>You have been assigned a new task by {created_by_name}.</p>
                <div class="task-card">
                    <h3>{task_title}</h3>
                    <p><strong>Due Date:</strong> {due_date}</p>
                    <p><strong>Assigned by:</strong> {created_by_name}</p>
                </div>
                <center>
                    <a href="{task_link}" class="button">View Task Details</a>
                </center>
                <p>Please review the task details and ensure timely completion.</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from Nigcomsat Performance Management System</p>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(
            to=[user_email],
            subject=f"New Task Assigned: {task_title}",
            html=html
        )

    @staticmethod
    def send_task_submitted_email(creator_email: str, creator_name: str, task_title: str, submitted_by_name: str):
        """Send task submission notification to creator"""
        task_link = f"{FRONTEND_URL}/dashboard/tasks"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: #10b981;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 500;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 8px 8px;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Task Submitted for Review</h1>
            </div>
            <div class="content">
                <p>Hello {creator_name},</p>
                <p><strong>{submitted_by_name}</strong> has submitted the task <strong>"{task_title}"</strong> for your review.</p>
                <center>
                    <a href="{task_link}" class="button">Review Task</a>
                </center>
                <p>Please review the submission and provide feedback.</p>
            </div>
            <div class="footer">
                <p>This is an automated notification from Nigcomsat Performance Management System</p>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(
            to=[creator_email],
            subject=f"Task Submitted: {task_title}",
            html=html
        )

    @staticmethod
    def send_task_reviewed_email(assignee_email: str, assignee_name: str, task_title: str, score: int, feedback: str, approved: bool):
        """Send task review notification to assignee"""
        task_link = f"{FRONTEND_URL}/dashboard/tasks"
        status = "Approved" if approved else "Needs Revision"
        color = "#10b981" if approved else "#f59e0b"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, {color} 0%, {color} 100%);
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .header h1 {{
                    color: white;
                    margin: 0;
                    font-size: 24px;
                }}
                .content {{
                    background: #ffffff;
                    padding: 30px;
                    border: 1px solid #e5e7eb;
                    border-top: none;
                }}
                .score-box {{
                    background: #f9fafb;
                    border-left: 4px solid {color};
                    padding: 20px;
                    margin: 20px 0;
                    border-radius: 6px;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 30px;
                    background: {color};
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                    font-weight: 500;
                }}
                .footer {{
                    background: #f9fafb;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 8px 8px;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Task Reviewed: {status}</h1>
            </div>
            <div class="content">
                <p>Hello {assignee_name},</p>
                <p>Your task <strong>"{task_title}"</strong> has been reviewed.</p>
                <div class="score-box">
                    <p><strong>Status:</strong> {status}</p>
                    <p><strong>Score:</strong> {score}/10</p>
                    {f'<p><strong>Feedback:</strong> {feedback}</p>' if feedback else ''}
                </div>
                <center>
                    <a href="{task_link}" class="button">View Task Details</a>
                </center>
            </div>
            <div class="footer">
                <p>This is an automated notification from Nigcomsat Performance Management System</p>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(
            to=[assignee_email],
            subject=f"Task Reviewed: {task_title} - {status}",
            html=html
        )
