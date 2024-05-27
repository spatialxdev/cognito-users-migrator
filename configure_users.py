import boto3

# Initialize Cognito client
region_name = 'us-east-1'
cognito_client = boto3.client('cognito-idp', region_name=region_name)


# Step 1: Get all users from AWS Cognito user pool
def get_all_users(user_pool_id):
    users = []
    response = cognito_client.list_users(UserPoolId=user_pool_id)
    users.extend(response['Users'])
    while 'PaginationToken' in response:
        response = cognito_client.list_users(UserPoolId=user_pool_id, PaginationToken=response['PaginationToken'])
        users.extend(response['Users'])
    return users


# Step 2: Create a dictionary of email and password pairs, and another dictionary for email and group pairs
passwords_to_change = {
    'user@example.com': 'my_password'
}

emails_to_group = {
    'user@example.com': 'my_group'
}


# Step 3: Change passwords for users whose email is in the dictionary
def change_passwords(user_pool_id, users):
    for user in users:
        for attr in user['Attributes']:
            if attr['Name'] == 'email' and attr['Value'] in passwords_to_change:
                username = user['Username']
                new_password = passwords_to_change[attr['Value']]
                cognito_client.admin_set_user_password(
                    UserPoolId=user_pool_id,
                    Username=username,
                    Password=new_password,
                    Permanent=True
                )
                print(f"Changed password for user {username} with email {attr['Value']} to {new_password}")


# Step 4: Attach users to groups based on their email addresses
def attach_users_to_groups(user_pool_id, users):
    for user in users:
        for attr in user['Attributes']:
            if attr['Name'] == 'email' and attr['Value'] in emails_to_group:
                group_name = emails_to_group[attr['Value']]
                create_group_if_not_exists(user_pool_id, group_name)
                username = user['Username']
                cognito_client.admin_add_user_to_group(
                    UserPoolId=user_pool_id,
                    Username=username,
                    GroupName=group_name
                )
                print(f"Attached user {username} with email {attr['Value']} to group {group_name}")


# Step 5: Create a group if it does not exist
def create_group_if_not_exists(user_pool_id, group_name):
    try:
        cognito_client.create_group(GroupName=group_name, UserPoolId=user_pool_id)
        print(f"Created group: {group_name}")
    except cognito_client.exceptions.GroupExistsException:
        print(f"Group already exists: {group_name}")


# Main function
def main():
    user_pool_id = 'user_pool_id'
    users = get_all_users(user_pool_id)
    change_passwords(user_pool_id, users)
    attach_users_to_groups(user_pool_id, users)


if __name__ == "__main__":
    main()
