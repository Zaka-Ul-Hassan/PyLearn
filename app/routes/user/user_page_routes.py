# app/routes/user/user_page.py

from io import BytesIO
import os
from fastapi import APIRouter, Form, HTTPException, Request, Depends
from fastapi.params import Query
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import pdfkit
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from app.services.authentication.auth_service import get_current_user
from app.utils.file_util import BASE_DIR, senitize_email_html
from app.models.user.user import User
from app.models.resume.resume_model import Resume
from app.db import get_db
from load_env import FRONTEND_BASE_URL

templates = Jinja2Templates(directory="frontend/templates")

# This adds FRONTEND_BASE_URL to every single template automatically
templates.env.globals.update(FRONTEND_BASE_URL=FRONTEND_BASE_URL)

router = APIRouter()

@router.get("/.well-known/appspecific/com.chrome.devtools.json")
async def chrome_devtools_json():
    return {"message": "Not used"}

@router.get("/", response_class=HTMLResponse)
def show_login(request: Request):
    return templates.TemplateResponse(request, "user/login.html", {
        "hide_navbar": True,
        "hide_footer": True,
        "fullscreen": True,
        "hide_sidebar": True,
        "hide_resume": True
    })

@router.get("/register")
def show_register_form(request: Request):
    return templates.TemplateResponse(request, "user/register.html", {
        "hide_navbar": True,
        "hide_footer": True,
        "fullscreen": True,
        "hide_sidebar": True,
        "hide_resume": True
    })

@router.get("/dashboard", response_class=HTMLResponse)
def show_dashboard(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Dashboard page - authentication is checked client-side via JavaScript
    The page is rendered without backend auth check, then JS verifies the token
    """
    # Create a minimal user object for template rendering
    # The actual auth check happens in JavaScript
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(request, "shared/dashboard/dashboard.html", {
        "user": minimal_user,
        "hide_resume": True
    })

@router.get("/resume-upload", response_class=HTMLResponse)
async def upload_resume(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Resume upload page - authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(request, "resume/resume-upload.html", {
        "user": minimal_user,
        "hide_resume": False
    })


@router.get("/job/list", response_class=HTMLResponse)
async def job_list_page(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Job list page - authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(request, "job/list.html", {
        "user": minimal_user,
        "resume_id": None,
        "hide_resume": True,
    })

@router.get("/job/linkedin", response_class=HTMLResponse)
async def linkedin_job_page(
    request: Request,
    db: Session = Depends(get_db),
):
    
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }

    return templates.TemplateResponse(request, "job/linkedin_job.html", {
        "user": minimal_user,
        "hide_resume": True,
    })

@router.get("/forgot-password", response_class=HTMLResponse)
def forgot_password(request: Request):
    return templates.TemplateResponse(request, "user/forgot_password.html", {
        "hide_navbar": True,
        "hide_footer": True,
        "fullscreen": True,
        "hide_sidebar": True
    })

@router.get("/reset-request-sent", response_class=HTMLResponse)
def reset_request_sent(request: Request, email: str):
    return templates.TemplateResponse(request, "user/reset_request_sent.html", {
        "email": email,
        "hide_navbar": True,
        "hide_footer": True,
        "fullscreen": True,
        "hide_sidebar": True
    })

# ========== USER MANAGEMENT ROUTE ==========

@router.get("/user/manage", response_class=HTMLResponse)
async def user_management_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    User Management Page - For SuperAdmin only
    Shows list of all users with create, update, delete, activate/deactivate functionality
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "user/user_management.html",
        {
            "user": minimal_user,
            "hide_resume": True
        }
    )

@router.get("/user/reset-password", response_class=HTMLResponse)
def reset_password_form(request: Request, token: str = Query(...)):
    return templates.TemplateResponse(
        request,
        "user/reset_password.html",
        {
            "token": token,
            "hide_navbar": True,
            "hide_footer": True,
            "fullscreen": True,
            "hide_sidebar": True
        }
    )

@router.get("/user/set-password", response_class=HTMLResponse)
def set_password_form(request: Request, token: str = Query(...)):
    return templates.TemplateResponse(
        request,
        "user/set_password.html",
        {
            "token": token,
            "hide_navbar": True,
            "hide_footer": True,
            "fullscreen": True,
            "hide_sidebar": True
        }
    )

# ========== UPDATE PROFILE ROUTE (MUST BE BEFORE /user/{user_id}) ==========

@router.get("/user/update-profile", response_class=HTMLResponse)
async def update_profile_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Update Profile Page - Edit user profile information
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "user/update_profile.html",
        {
            "user": minimal_user,
            "hide_resume": True
        }
    )


# ========== CHANGE PASSWORD ROUTE (MUST BE BEFORE /user/{user_id}) ==========

@router.get("/user/change-password", response_class=HTMLResponse)
async def change_password_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Change Password Page - Update user password
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "user/change_password.html",
        {
            "user": minimal_user,
            "hide_resume": True
        }
    )

# ========== PARAMETERIZED USER ROUTE (MUST COME AFTER ALL SPECIFIC /user/* ROUTES) ==========

@router.get("/user/{user_id}", response_class=HTMLResponse)
def profile_page(
    request: Request,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    User profile edit page
    This endpoint requires authentication
    """
    # Ensure user is accessing their own profile (or admin check)
    if current_user.data.Id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    resume = db.query(Resume).filter(Resume.UserId == user_id, Resume.IsDeleted == False).first()

    return templates.TemplateResponse(request, "profile/edit_profile.html", {
        "user": current_user,
        "resume": resume
    })

# ========== EMAIL ROUTES ==========

@router.get("/email/settings", response_class=HTMLResponse)
async def email_settings_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Email Settings Page - Configure SMTP settings for sending emails
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "email/email_settings.html",
        {
            "user": minimal_user,
            "hide_resume": True
        }
    )


@router.get("/email/compose-email", response_class=HTMLResponse)
async def compose_email_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Compose Email Page - Send emails to recipients
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "email/compose_email.html",
        {
            "user": minimal_user,
            "hide_resume": True
        }
    )


@router.get("/email/sent", response_class=HTMLResponse)
async def sent_email_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Sent Emails Page - View sent emails with pagination and search
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "email/sent_email.html",
        {
            "user": minimal_user,
            "hide_resume": True
        }
    )


@router.get("/email/inbox", response_class=HTMLResponse)
async def inbox_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Email Inbox Page - View received/replied emails
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "email/email_inbox.html",
        {
            "user": minimal_user,
            "hide_resume": True
        }
    )

# ========== RESUME ROUTES - SPECIFIC ROUTES MUST COME BEFORE PARAMETERIZED ROUTES ==========

@router.get("/resume/list", response_class=HTMLResponse)
async def resume_list_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Resume List Page - Browse all resumes in database
    Shows all available resumes with search and filter functionality
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    # Fetch all active resumes ordered by newest first
    resumes = db.query(Resume).filter(
        Resume.IsDeleted == False
    ).order_by(Resume.CreatedAt.desc()).all()

    return templates.TemplateResponse(
        request,
        "resume/resume_list.html",
        {
            "user": minimal_user,
            "resumes": resumes,
            "hide_resume": False
        }
    )


@router.get("/resume/rag", response_class=HTMLResponse)
async def resume_rag_page(
    request: Request
):
    """
    AI Candidate Finder - RAG-based chatbot interface
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "resume/resume_rag.html",
        {
            "user": minimal_user
        }
    )

@router.get("/resume/manage", response_class=HTMLResponse)
async def resume_manage_page(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Render the resume CRUD management page
    Authentication checked client-side
    """
    minimal_user = {
        "Id": None,
        "FirstName": "",
        "LastName": "",
        "Email": "",
        "Address": "",
        "Image": None
    }
    
    return templates.TemplateResponse(
        request,
        "resume/resume_crud.html",
        {
            "user": minimal_user
        }
    )


@router.get("/resume/download/{user_id}")
def download_resume_route(
    user_id: int,
    db: Session = Depends(get_db)
):

    # Fetch resume
    resume = db.query(Resume).filter(Resume.UserId == user_id, Resume.IsDeleted == False).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Build clean HTML with only non-empty fields
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.5; color: #000;">
            <h3 style="text-align: center;">{resume.FullName}</h3>
            <p style="text-align: center;">
                {resume.Email if resume.Email else ""} 
                {("|" if resume.Email and resume.PhoneNumber else "")} 
                {resume.PhoneNumber if resume.PhoneNumber else ""} 
                {("|" if (resume.Email or resume.PhoneNumber) and resume.Address else "")} 
                {resume.Address if resume.Address else ""}
            </p>
            <hr>
            
            {"<h3>Objective</h3><p>" + resume.Objective + "</p>" if resume.Objective else ""}
            {"<h3>Summary</h3><p>" + resume.Summary + "</p>" if resume.Summary else ""}
            
            {"<h3>Education</h3><ul>" +
             ("<li>" + resume.Education1 + "</li>" if resume.Education1 else "") +
             ("<li>" + resume.Education2 + "</li>" if resume.Education2 else "") +
             ("<li>" + resume.Education3 + "</li>" if resume.Education3 else "") +
             "</ul>" if resume.Education1 or resume.Education2 or resume.Education3 else ""}
            
            {"<h3>Skills</h3><p>" + resume.Skills + "</p>" if resume.Skills else ""}
            
            {"<h3>Experience</h3><p>" + resume.ExperienceDescription + "</p>" if resume.ExperienceDescription else ""}
            {"<p><strong>Total Experience:</strong> " + resume.TotalExperience + "</p>" if resume.TotalExperience else ""}
            
            {"<h3>Projects</h3><ul>" +
             ("<li>" + resume.Project1 + "</li>" if resume.Project1 else "") +
             ("<li>" + resume.Project2 + "</li>" if resume.Project2 else "") +
             "</ul>" if resume.Project1 or resume.Project2 else ""}
            
            {("<h3>Certifications</h3><p>" + resume.Certifications + "</p>") if resume.Certifications else ""}
            {("<h3>Languages</h3><p>" + resume.Languages + "</p>") if resume.Languages else ""}
        </body>
    </html>
    """

    # Configure pdfkit
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    options = {
        'no-images': '',
        'disable-javascript': '',
        'disable-smart-shrinking': '',
        'enable-local-file-access': ''
    }

    # Generate PDF
    pdf_bytes = pdfkit.from_string(html_content, False, configuration=config, options=options)

    safe_name = resume.FullName.replace(" ", "_")
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={safe_name}_Resume.pdf"}
    )


@router.get("/resume/{user_id}", response_class=HTMLResponse)
def view_resume_page(
    request: Request,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    View resume page (HTML display)
    This endpoint requires authentication
    """
    # Ensure user is accessing their own resume (or admin check)
    if current_user.data.Id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    resume = db.query(Resume).filter(Resume.UserId == user_id, Resume.IsDeleted == False).first()

    return templates.TemplateResponse(request, "resume/get_resume.html", {
        "user": current_user,
        "resume": resume
    })