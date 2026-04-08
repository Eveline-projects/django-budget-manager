from django.contrib.auth.tokens import PasswordResetTokenGenerator

class AccountActivationTokenGen(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) + str(user.is_active)
        )

acc_activation_token = AccountActivationTokenGen()