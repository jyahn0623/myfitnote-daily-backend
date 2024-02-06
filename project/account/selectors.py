from account.models import *

class UserSelector:
    
    def get_client_by_company(self, company):
        """Get client list by company"""
        clients = Client.objects.filter(manager__company=company)
        return clients
    
    def get_manager_by_company(self, company):
        """Get manager list by company"""
        managers = CompanyManager.objects.filter(company=company)
        return managers
    
    
