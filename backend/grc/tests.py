from django.test import TestCase
from rest_framework.test import APIClient
from .models import Audit, AuditFinding
from django.utils import timezone

# Create your tests here.

class AuditVersioningTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test data
        self.audit = Audit.objects.create(
            Status='Under review',
            ReviewStatus=0
        )
        self.finding = AuditFinding.objects.create(
            AuditId=self.audit,
            ComplianceId=1,
            Check='1'
        )

    def test_version_flow(self):
        """Test the complete version flow"""
        # Initial submission (A1)
        response = self.client.post(f'/audits/{self.audit.AuditId}/submit/')
        self.assertEqual(response.data['version'], 'A1')

        # First review (R1)
        response = self.client.post(f'/audits/{self.audit.AuditId}/save-review/', {
            'review_status': 'Reject'
        })
        self.assertEqual(response.data['version'], 'R1')

        # Post-rejection update (A2)
        self.audit.ReviewStatus = 3  # Set as rejected
        self.audit.save()
        response = self.client.post(f'/audit-findings/{self.finding.ComplianceId}/', {
            'status': '2'
        })
        self.assertTrue(response.data['new_version_created'])
        self.assertTrue('A2' in response.data.get('version', ''))

    def test_multiple_rejections(self):
        """Test multiple rejection cycles"""
        versions = ['A1', 'R1', 'A2', 'R2', 'A3']
        current_status = 0  # Start with Under Review

        for expected_version in versions:
            if expected_version.startswith('A'):
                # Auditor update
                response = self.client.post(f'/audit-findings/{self.finding.ComplianceId}/', {
                    'status': '2'
                })
            else:
                # Reviewer rejection
                response = self.client.post(f'/audits/{self.audit.AuditId}/save-review/', {
                    'review_status': 'Reject'
                })
                current_status = 3  # Set as rejected

            self.audit.ReviewStatus = current_status
            self.audit.save()
            
            self.assertEqual(response.data.get('version', ''), expected_version)

    def test_version_integrity(self):
        """Test that versions maintain their integrity"""
        # Create initial version
        response = self.client.post(f'/audits/{self.audit.AuditId}/submit/')
        initial_version = response.data['version']

        # Get the version data
        response = self.client.get(f'/audits/{self.audit.AuditId}/versions/{initial_version}/')
        initial_data = response.data['findings']

        # Make changes after rejection
        self.audit.ReviewStatus = 3
        self.audit.save()
        response = self.client.post(f'/audit-findings/{self.finding.ComplianceId}/', {
            'status': '2'
        })
        new_version = response.data['version']

        # Verify initial version remains unchanged
        response = self.client.get(f'/audits/{self.audit.AuditId}/versions/{initial_version}/')
        self.assertEqual(response.data['findings'], initial_data)
