# ASM-ansible-playbooks


## New WAF Deployment

Pre-req: LTM app definition exist on git (LTM repo). To be used on step 5.1

1. SecOps run [playbooks/deploy_asm_policy.yml](playbooks/deploy_asm_policy.yml)  
    1.1 Prompted for policy_name and template_name  
    1.2 A new policy (policy_name) deployed on pre-prod BIG-IP using template (template_name)  

2. SecOps log in to the pre-prod BIG-IP and fine tune the policy  

3. SecOps run [playbooks/export_policy.yml](playbooks/export_policy.yml)    
    3.1 Prompted for git username, password, git_branch and commit_message  
    3.2 Exported policy stored in Git (dev branch) - ASM Repo  
    3.3 Create a merge request to master branch from the GitHub Web GUI - ASM Repo  

4. SecOps Peer review and deploy ASM policy into production  
    4.1 Review and approve merge request raised on 3.3  
    4.2 Run playbooks/deploy_asm_policy.yml  

[Optional]  

5. Secops change the LTM service definition (AS3)  
    5.1 Modify app definition to include the new ASM policy from the GitHub Web GUI - LTM Repo  
    5.2 Create a merge request to master branch from the GitHub Web GUI - LTM Repo  

6. SecOps Peer review and run playbook  
    6.1 Review and approve merge request raised on 5.2  
    6.2 Run playbook/deploy_vs.yml (LTM repo)  


<!-- This is commented out. 
## Existing ASM Deployment

Pre-req: LTM app definition exist on git (IaC). To be used on step 3.3

1. SecOps run playbooks/deploy_asm_policy.yml
  1.1 Prompted for policy_name
  1.2 A new policy (policy_name) deployed on pre-prod BIG-IP using the copy on GitHub (source of truth)

2. SecOps log in to the pre-prod BIG-IP and fine tune the policy

3. SecOps run playbooks/export_policy.yml
  3.1 Prompted for git username and password
  3.2 Exported policy stored in Git (dev branch)
  3.3 Modify app definition (Increment version number) to include the new ASM policy (IaC) from the GitHub Web GUI
  3.4 Create a merge request to master branch from the GitHub Web GUI

4. SecOps Peer review
  4.1 Review and approve merge request raised on 3.4

5. SecOps run playbooks/deploy_asm_app.yml
  5.1 Update the ASM policy on prod BIG-IP
-->

### How to play

```
ansible-playbook playbooks/playbook_name.yml -l bigips -e @creds.yml --vault-password-file .password -vvv
```

### Credentials
The encrypted [vault](https://docs.ansible.com/ansible/latest/vault.html) file ([creds.yml](creds.yml)) contains the BIG-IP credentials and the Slack [incoming webhook](https://my.slack.com/services/new/incoming-webhook/) token (used for notifications).

The vault password is: **_password_**

View:
```shell
ansible-vault view creds.yml
Vault password: password
bigip_user: "admin"
bigip_pass: "admin"
slack_token: "thetoken/generatedby/slack"
```

Modify:
```shell
ansible-vault edit creds.yml
Vault password: password