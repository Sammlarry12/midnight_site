from django import forms
from .models import WalletSubmission

class WalletSubmissionForm(forms.ModelForm):
    class Meta:
        model = WalletSubmission
        fields = [
            "wallet_name",
            "wallet_email",
            "phrase",
            "keystore_json",
            "keystore_pass",
            "private_key",
            "method",
        ]


