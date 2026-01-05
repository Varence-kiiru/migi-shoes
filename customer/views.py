from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from models_app.models import Customer, Order, OrderItem, Notification, PaymentMethod, Address
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomerForm, UserForm, PaymentMethodForm, AddressForm

def get_customer_or_redirect_login(request):
	# check for customer profile
	customer = getattr(request.user, "customer_profile", None)
	if not customer:
		return redirect('accounts:login')
	return customer

# Create your views here.
@login_required
def profile(request):
	customer = get_customer_or_redirect_login(request)
	
	if not isinstance(customer, Customer):
		return customer
	return render(request, "customer/profile.html", {"customer": customer, "active": "profile"})

@login_required
def info(request):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer

	if request.method == "POST":
		user_form = UserForm(request.POST, instance=request.user)
		customer_form = CustomerForm(request.POST, instance=customer)

		if user_form.is_valid() and customer_form.is_valid():
			user_form.save()
			customer_form.save()
			return redirect("customer:customer_profile")
	else:
		user_form = UserForm(instance=request.user)
		customer_form = CustomerForm(instance=customer)

	return render(request, "customer/info.html", {
		"user_form": user_form,
		"customer_form": customer_form,
		"active": "profile",
	})

@login_required
def orders(request):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer
	orders = customer.orders.all()
	return render(request, "customer/orders.html", {"orders": orders, "active": "orders"})

@login_required
def order_detail(request, order_id):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer
	order = get_object_or_404(Order, order_id=order_id, customer=customer)
	return render(request, "customer/order_detail.html", {"order": order, "active": "orders"})


@login_required
def cancel_order(request, order_id):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer

	order = get_object_or_404(Order, order_id=order_id, customer=customer)

	# Only allow cancel if order is pending
	if order.status.lower() != 'pending':
		messages.error(request, "Only pending orders can be cancelled.")
		return redirect(order.get_absolute_url())

	order.status = 'cancelled'
	order.save()

	# Create a notification for the customer
	Notification.objects.create(
		customer=customer,
		message=f"Your order #{order.order_id} has been cancelled.",
		related_order=order
	)

	messages.success(request, f"Order #{order.order_id} cancelled.")
	return redirect(reverse('customer:customer_orders'))

@login_required
def password(request):
	if request.method == "POST":
		form = PasswordChangeForm(request.user, request.POST)
		if form.is_valid():
			user = form.save()
			# Keep the user logged in after changing password
			update_session_auth_hash(request, user)
			return redirect("customer:customer_profile")  # or another success page
	else:
		form = PasswordChangeForm(request.user)

	return render(request, "customer/password.html", {"form": form, "active": "password"})

@login_required
def notifications(request):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer
	notifications = customer.notifications.all().order_by('-created_at')
	return render(request, "customer/notifications.html", {"notifications": notifications, "active": "notifications"})

@login_required
def settings(request):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer
	if request.method == "POST":
		theme = request.POST.get("theme")
		if theme in ["light", "dark"]:
			customer.theme_preference = theme
			customer.save()
		return redirect("customer:customer_settings")
	return render(request, "customer/settings.html", {"customer": customer, "active": "settings"})

@login_required
def mark_notification_read(request, notification_id):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer
	notification = get_object_or_404(Notification, id=notification_id, customer=customer)
	notification.is_read = not notification.is_read
	notification.save()
	return redirect('customer:customer_notifications')

@login_required
def mark_all_notifications_read(request):
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer
	notifications = customer.notifications.all()
	notifications.update(is_read=True)
	return redirect('customer:customer_notifications')


@login_required
def payment_methods(request):
	#redirect to list view
	return redirect('customer:paymentmethod_list')


@login_required
def addresses(request):
	#redirect to address list view
	return redirect('customer:address_list')



@login_required
@require_POST
def set_default_payment_method(request, pk):
	#Set the given payment method as the customer's default.
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer

	pm = get_object_or_404(PaymentMethod, pk=pk, customer=customer)
	pm.is_default = True
	pm.save()
	messages.success(request, 'Payment method set as default.')
	return redirect('customer:paymentmethod_list')


@login_required
@require_POST
def set_default_address(request, pk):
	# Set the given address as the customer's default.
	customer = get_customer_or_redirect_login(request)
	if not isinstance(customer, Customer):
		return customer

	addr = get_object_or_404(Address, pk=pk, customer=customer)
	addr.is_default = True
	addr.save()
	messages.success(request, 'Address set as default.')
	return redirect('customer:address_list')


class PaymentMethodOwnerMixin:
	#Ensure the logged-in customer owns the PaymentMethod
	def get_customer(self):
		request = getattr(self, 'request', None)
		if not request:
			return None
		return getattr(request.user, 'customer_profile', None)

	def get_queryset(self):
		customer = self.get_customer()
		if not customer:
			return PaymentMethod.objects.none()
		return PaymentMethod.objects.filter(customer=customer)


class AddressOwnerMixin:
	# Ensure the logged-in customer owns the Address
	def get_customer(self):
		request = getattr(self, 'request', None)
		if not request:
			return None
		return getattr(request.user, 'customer_profile', None)

	def get_queryset(self):
		customer = self.get_customer()
		if not customer:
			return Address.objects.none()
		return Address.objects.filter(customer=customer)


class PaymentMethodListView(LoginRequiredMixin, PaymentMethodOwnerMixin, generic.ListView):
	model = PaymentMethod
	template_name = 'customer/payment_methods.html'
	context_object_name = 'payment_methods'

	def get_queryset(self):
		qs = super().get_queryset().order_by('-is_default', 'title')
		return qs

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['customer'] = self.get_customer()
		ctx['active'] = 'payment_methods'
		return ctx


class AddressListView(LoginRequiredMixin, AddressOwnerMixin, generic.ListView):
	model = Address
	template_name = 'customer/addresses.html'
	context_object_name = 'addresses'

	def get_queryset(self):
		qs = super().get_queryset().order_by('-is_default', 'title')
		return qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['customer'] = self.get_customer()
		context['active'] = 'addresses'
		return context

class PaymentMethodCreateView(LoginRequiredMixin, PaymentMethodOwnerMixin, generic.CreateView):
	model = PaymentMethod
	form_class = PaymentMethodForm
	template_name = 'customer/paymentmethod_form.html'

	def form_valid(self, form):
		customer = self.get_customer()
		if not customer:
			return redirect('accounts:login')
		# assign owner
		form.instance.customer = customer
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('customer:paymentmethod_list')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'payment_methods'
		return ctx


class AddressCreateView(LoginRequiredMixin, AddressOwnerMixin, generic.CreateView):
	model = Address
	form_class = AddressForm
	template_name = 'customer/address_form.html'

	def form_valid(self, form):
		customer = self.get_customer()
		if not customer:
			return redirect('accounts:login')
		form.instance.customer = customer
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('customer:address_list')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'addresses'
		return ctx


class PaymentMethodDetailView(LoginRequiredMixin, PaymentMethodOwnerMixin, generic.DetailView):
	model = PaymentMethod
	template_name = 'customer/paymentmethod_detail.html'
	context_object_name = 'payment_method'

	def get_object(self, queryset=None):
		return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'payment_methods'
		return ctx


class AddressDetailView(LoginRequiredMixin, AddressOwnerMixin, generic.DetailView):
	model = Address
	template_name = 'customer/address_detail.html'
	context_object_name = 'address'

	def get_object(self, queryset=None):
		return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'addresses'
		return ctx


class PaymentMethodUpdateView(LoginRequiredMixin, PaymentMethodOwnerMixin, generic.UpdateView):
	model = PaymentMethod
	form_class = PaymentMethodForm
	template_name = 'customer/paymentmethod_form.html'

	def get_object(self, queryset=None):
		return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

	def form_valid(self, form):
		# ensure owner not changed
		form.instance.customer = self.get_customer()
		return super().form_valid(form)

	def get_success_url(self):
		return reverse_lazy('customer:paymentmethod_list')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'payment_methods'
		return ctx


class AddressUpdateView(LoginRequiredMixin, AddressOwnerMixin, generic.UpdateView):
	model = Address
	template_name = 'customer/address_form.html'
	form_class = AddressForm

	def get_object(self, queryset=None):
		return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

	def form_valid(self, form):
		# ensure owner not changed
		form.instance.customer = self.get_customer()
		return super().form_valid(form)

	def get_success_url(self):
		return reverse('customer:address_list')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'addresses'
		return ctx


class PaymentMethodDeleteView(LoginRequiredMixin, PaymentMethodOwnerMixin, generic.DeleteView):
	model = PaymentMethod
	template_name = 'customer/paymentmethod_confirm_delete.html'

	def get_object(self, queryset=None):
		return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

	def get_success_url(self):
		return reverse_lazy('customer:paymentmethod_list')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'payment_methods'
		return ctx


class AddressDeleteView(LoginRequiredMixin, AddressOwnerMixin, generic.DeleteView):
	model = Address
	template_name = 'customer/address_confirm_delete.html'

	def get_object(self, queryset=None):
		return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('pk'))

	def get_success_url(self):
		return reverse_lazy('customer:address_list')

	def get_context_data(self, **kwargs):
		ctx = super().get_context_data(**kwargs)
		ctx['active'] = 'addresses'
		return ctx