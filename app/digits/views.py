from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ImageForm
from .neural.preprocessing import preprocess_image
from .neural.model import GACNN


class UserAuthMixin(UserPassesTestMixin):
    """Prevents unauthenticated users from using a view."""
    def test_func(self):
        return self.request.user.is_authenticated


class HomeView(UserAuthMixin, FormView):
    """
    The home view, allows for image upload if the user is authenticated.
    Redirects unauthenticated users to the "unauthorized" page.
    """
    template_name = "home.html"
    form_class = ImageForm
    success_url = reverse_lazy("home")
    login_url = reverse_lazy("unauthorized")

    def form_valid(self, form: ImageForm):
        """
        This method is called when the form data is valid.
        Preprocesses the image and inputs it into the model for classification.
        Sets "digit_is_valid" to True and "digit" to the detected digit in the site context.
        :param form: The form that was validated.
        :return: Response
        """

        # load image
        f = form.cleaned_data["image"]
        img = preprocess_image(f.file)

        # input into model
        model = GACNN.get_trained()
        digit = model.classify_input(img)

        context = self.get_context_data(form=form)
        context["digit_is_valid"] = True
        context["digit"] = digit

        return self.render_to_response(context)
