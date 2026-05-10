"""
Member Management JSON API.
Provides RESTful endpoints for CRUD operations on the Member model.
"""
from flask import Blueprint, request, jsonify
from app.models.member import Member
from app.utils.db import db

# Initialize the Blueprint for the Member API
member_api_bp = Blueprint('member_api', __name__)

@member_api_bp.route('/api/members', methods=['GET'])
def get_members():
    """
    Retrieves all library members and returns them as a JSON array.
    """
    members = Member.query.all()
    member_list = [{
        'id': member.id,
        'full_name': member.full_name,
        'email': member.email,
        'phone': member.phone,
        'address': member.address,
        'membership_date': member.membership_date.strftime("%Y-%m-%d %H:%M") if member.membership_date else None
    } for member in members]
    
    return jsonify(member_list)

@member_api_bp.route('/api/members', methods=['POST'])
def add_member():
    """
    Adds a new member record from JSON input.
    """
    data = request.get_json()
    
    if not data or not data.get('full_name') or not data.get('email'):
        return jsonify({'error': 'Full Name and Email are required fields'}), 400

    new_member = Member(
        full_name=data.get('full_name'),
        email=data.get('email'),
        phone=data.get('phone'),
        address=data.get('address')
    )

    try:
        db.session.add(new_member)
        db.session.commit()
        return jsonify({'message': 'Member added successfully', 'member_id': new_member.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@member_api_bp.route('/api/members/<int:id>', methods=['PUT'])
def update_member(id):
    """
    Updates an existing member record based on JSON input.
    """
    member = Member.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided for update'}), 400

    # Selective updates
    if 'full_name' in data: member.full_name = data['full_name']
    if 'email' in data: member.email = data['email']
    if 'phone' in data: member.phone = data['phone']
    if 'address' in data: member.address = data['address']

    try:
        db.session.commit()
        return jsonify({'message': 'Member updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@member_api_bp.route('/api/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    """
    Deletes a member record from the system.
    """
    member = Member.query.get_or_404(id)
    try:
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
