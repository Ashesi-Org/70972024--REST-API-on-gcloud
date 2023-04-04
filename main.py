'''author: Reynolds Okyere Boakye'''

import json
from flask import Flask, request, jsonify, escape
import functions_framework
import firebase_admin
from firebase_admin import credentials, firestore

app = firebase_admin.initialize_app()
db = firestore.client()


# main running function
@functions_framework.http
def ashesi(request):
    if request.path == '/' or request.path == '/student':
        if request.method == 'GET':
            return retrieve_student(request)
        elif request.method == 'POST':
            return create_student(request)
        elif request.method == 'PATCH':
            return update_student(request)
        elif request.method == 'DELETE':
            return delete_student(request)
        else:
            from flask import abort
            return abort(405)
        
    elif request.path == '/election':
        if request.method == 'GET':
            return retrieve_election(request)
        elif request.method == 'POST':
            return create_election(request) 
        elif request.method == 'DELETE':
            return delete_election(request)    
        elif request.method == 'PATCH':
            return vote_in_election(request)
        else:
            from flask import abort
            return abort(405)
            
    else:
        from flask import abort
        return abort(403)

# search for a sudent
def retrieve_student(request):   
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    if request_json and 'id' in request_json:
        student_id = int(request_json['id'])
    elif request_args and 'id' in request_args:
        student_id = int(request_args['id'])
    else:
        return 'Specify ID',404
        
    student_ref = db.collection('students')
    students = student_ref.stream()    
    
    for student in students:
        result = student.to_dict()
        if result['id'] == student_id:
            return result
            
    return 'No student with this ID found',404


#create a new voter
def create_student(request):
    request_json = request.get_json(silent=True)
    
    if request_json and 'id' in request_json:
        student_id = request_json['id']
    else:
        return 'Specify ID',404
    
    student_ref = db.collection('students')
    students = student_ref.stream()   

    for student in students:
        if student.to_dict()['id'] == student_id:
            return f"{escape(student_id)} already exists",404
    
    student_ref = student_ref.document(str(student_id))
    student_ref.set(request_json)  
        
    return f"{escape(student_id)}'s record is added"
    

#update an existing voter
def update_student(request):
    request_json = request.get_json(silent=True)
    
    if request_json and 'id' in request_json:
        student_id = request_json['id']
    else:
        return 'Specify ID',404
        
    students_ref = db.collection('students')
    students = students_ref.stream()    
    
    for student in students:
        result = student.to_dict()
        if result['id'] == student_id:
            update = students_ref.document(str(student_id))
            # make the necessary changes only in the different information
            for key, value in request_json.items():                
                if key not in result or value != result[key]:
                    update.update({key:value})
        
            return f"{escape(student_id)}'s record is updated"
             
    return  f"{escape(student_id)} not found",404
    
    
# delete a voter  
def delete_student(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    if request_json and 'id' in request_json:
        student_id = request_json['id']
    elif request_args and 'id' in request_args:
        student_id = request_args['id']
    else:
        return 'Specify ID',404
        
    students_ref = db.collection('students')
    students = students_ref.stream()    
    
    for student in students:
        result = student.to_dict()
        if result['id'] == student_id:
            students_ref.document(str(student_id)).delete()
            return f"Student deleted: {escape(student_id)}"
        
    return f"{escape(student_id)} not found", 404


#for the election

#retrieve an election
def retrieve_election(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    if request_json and 'id' in request_json:
        election_id = int(request_json['id'])
    elif request_args and 'id' in request_args:
        election_id = int(request_args['id'])
    else:
        return 'Specify ID',404
        request.path.startwith
    election_ref = db.collection('elections')
    elections = election_ref.stream()    
    
    for election in elections:
        result = election.to_dict()
        if result['election_id'] == election_id:
            return result
            
    return 'No voter with this ID found',404

#create a new election
def create_election(request):
    request_json = request.get_json(silent=True)
    
    if request_json and ('id' in request_json and 'title' in request_json):
        election_id = request_json['id']
        title = request_json['title']
    else:
        return 'Specify ID and title',404
        
    elections_ref = db.collection('elections')
    elections = elections_ref.stream()    
    
    for election in elections:
        result = election.to_dict()
        if result['election_id'] == election_id:
            return 'Election already exists', 404
        
    elections_ref = elections_ref.document(str(election_id))
    elections_ref.set({"election_id": election_id, "title": title})  
    
    # setting the election information for voting
    elections_ref = db.collection('voting').document(str(election_id))
    if 'info' in request_json:
        elections_ref.set({"election_id": election_id, "info": list(request_json['info'])})
    else: 
        elections_ref.set({"election_id": election_id, "info": []})
            
    return f"Election ID: {escape(election_id)} is added to elections"


# delete an election  
def delete_election(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    if request_json and 'id' in request_json:
        election_id = request_json['id']
    elif request_args and 'id' in request_args:
        election_id = request_args['id']
    else:
        return 'Specify ID',404
        
    elections_ref = db.collection('elections')
    elections = elections_ref.stream()    
    
    voting_ref = db.collection('voting')
    
    for election in elections:
        result = election.to_dict()
        if result['election_id'] == election_id:
            elections_ref.document(str(election_id)).delete()
            voting_ref.document(str(election_id)).delete()
            return f"Election deleted: {escape(election_id)}"
        
    return f"Election {escape(election_id)} not found", 404


# registers a voter to vote in an election
def vote_in_election(request):
    request_json = request.get_json(silent=True)
    
    if request_json and ('election' in request_json and 'position' in request_json and 'candidate' in request_json and 'voter' in request_json):
        election_id = request_json['election']
        position_id = request_json['position']
        candidate_id = request_json['candidate']
        student_id = request_json['voter']
    else:
        return 'Provide election, position, candidate and voter ID',404
    
    # checks if election exists
    election_ref = db.collection('elections')
    elections = election_ref.stream()    
    found = False
    
    for election in elections:
        result = election.to_dict()
        if result['election_id'] == election_id:
            found = True
            break
            
    if not found:
        return 'No election with this ID found',404
        
    # checks if student exists
    student_ref = db.collection('students')
    students = student_ref.stream()    
    found = False
    
    for student in students:
        result = student.to_dict()
        if result['id'] == student_id:
            found = True
            break
            
    if not found:
        return 'No student with this ID found',404
      
    voting_ref = db.collection('voting')
    voting = voting_ref.stream()    
    
    for vote in voting:
        result = vote.to_dict()
        if result['election_id'] == election_id:
            info = result['info']
            
            for position in info:
                if position['position_id'] == position_id:
                    all_voters = position['voters']
                    
                    if student_id in all_voters:       
                        return f"student ({escape(student_id)}) has already voted"
                        
                    candidates = position['candidates']
                    
                    for cand in candidates:
                        if cand['candidate_id'] == candidate_id:
                            cand['votes'] += 1
                            all_voters.append(student_id)
                            
                            voting_ref.document(str(election_id)).update({'info':info})
                            
                            return f"{escape(student_id)} has casted vote in election ({election_id})"
                        
                    return f"no candidate with this {escape(candidate_id)}",404         
                    
            return f"no position with this {escape(position_id)}",404
                
    return  f"no election with this {escape(election_id)}",404



# app1.run(debug=True)