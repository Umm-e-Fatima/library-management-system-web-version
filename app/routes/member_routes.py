"""
Member Management Routes for Library Management System.
Implements CRUD operations and search functionality for the Member entity.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.member import Member
from app.utils.db import db

# Initialize the Blueprint for members
member_bp = Blueprint('members', __name__)

@member_bp.route('/members')
def view_members():
    """
    Displays a list of all library members.
    """
    members = Member.query.all()
    return render_template('members/view.html', members=members)

@member_bp.route('/members/add', methods=['GET', 'POST'])
def add_member():
    """
    Handles the registration of a new library member.
    """
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # Basic validation: ensure email uniqueness
        existing_member = Member.query.filter_by(email=email).first()
        if existing_member:
            flash('A member with this email already exists.', 'danger')
            return render_template('members/add.html')

        new_member = Member(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address
        )

        try:
            db.session.add(new_member)
            db.session.commit()
            flash('Member added successfully!', 'success')
            return redirect(url_for('members.view_members'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('members/add.html')

@member_bp.route('/members/edit/<int:id>', methods=['GET', 'POST'])
def update_member(id):
    """
    Updates the record for an existing member.
    """
    member = Member.query.get_or_404(id)

    if request.method == 'POST':
        member.full_name = request.form.get('full_name')
        member.email = request.form.get('email')
        member.phone = request.form.get('phone')
        member.address = request.form.get('address')

        try:
            db.session.commit()
            flash('Member updated successfully!', 'success')
            return redirect(url_for('members.view_members'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')

    return render_template('members/update.html', member=member)

@member_bp.route('/members/delete/<int:id>', methods=['POST'])
def delete_member(id):
    """
    Deletes a member record from the database.
    """
    member = Member.query.get_or_404(id)
    try:
        db.session.delete(member)
        db.session.commit()
        flash('Member deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')

    return redirect(url_for('members.view_members'))

@member_bp.route('/members/search')
def search_member():
    """
    Searches for members by name, email, or phone number.
    """
    query = request.args.get('query', '')
    if query:
        members = Member.query.filter(
            (Member.full_name.ilike(f'%{query}%')) |
            (Member.email.ilike(f'%{query}%')) |
            (Member.phone.ilike(f'%{query}%'))
        ).all()
    else:
        members = Member.query.all()

    return render_template('members/view.html', members=members, search_query=query)
