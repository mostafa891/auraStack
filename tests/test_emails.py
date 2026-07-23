import pytest
from django.core import mail
from django.template.loader import render_to_string


def test_welcome_email_template_rendering():
    """التحقق من صحة تصيير قالب البريد الإلكتروني الترحيبي والتأكد من تضمين المعاملات."""
    context = {"site_url": "http://localhost:8000"}
    html_content = render_to_string("emails/welcome.html", context)

    assert "Welcome aboard!" in html_content
    assert "http://localhost:8000/auth/login/" in html_content
    assert "AuraFlow" in html_content


def test_password_reset_email_template_rendering():
    """التحقق من صحة تصيير قالب بريد استعادة كلمة المرور والتأكد من إدراج رابط إعادة التعيين."""
    context = {"password_reset_url": "http://localhost:8000/reset-confirm/123/"}
    html_content = render_to_string("emails/password_reset.html", context)

    assert "Password Reset Request" in html_content
    assert "http://localhost:8000/reset-confirm/123/" in html_content


def test_workspace_invite_email_template_rendering():
    """التحقق من صحة تصيير قالب دعوات الأعضاء وإدراج اسم الداعي ومساحة العمل."""
    context = {
        "inviter": "Mohamed",
        "workspace_name": "DeepMind Corp",
        "invite_url": "http://localhost:8000/invite/accept/token123/",
    }
    html_content = render_to_string("emails/workspace_invite.html", context)

    assert "Mohamed" in html_content
    assert "DeepMind Corp" in html_content
    assert "http://localhost:8000/invite/accept/token123/" in html_content


@pytest.mark.django_db
def test_send_email_outbox_integration():
    """التحقق من أن استدعاء إرسال إيميل عبر دجانغو يضعه في الـ outbox بنجاح في التطوير."""
    mail.send_mail(
        subject="Test Email",
        message="Hello World",
        from_email="no-reply@auraflow.com",
        recipient_list=["user@example.com"],
        html_message="<h1>Hello World</h1>",
    )

    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "Test Email"
    assert "Hello World" in mail.outbox[0].body
