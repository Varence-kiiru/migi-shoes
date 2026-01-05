from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Avg, Sum
from models_app import models
from .forms import Reviewform
#from .models import Shoe,ShoeVariant,Review,OrderItem
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.http import Http404
#from django.http import HttpResponse

# Create your views here.

@login_required
def add_wishlist_item(request, shoe_id):
    if request.method != "POST":
        return redirect('products:shoe_details', shoe_id=shoe_id)

    shoe = get_object_or_404(models.Shoe, pk=shoe_id)
    customer = request.user.customer_profile if request.user.is_authenticated else None    
    
    if not customer:
        return redirect('products:shoe_details', shoe_id=shoe_id)

    models.WishlistItem.objects.get_or_create(customer=customer, shoe=shoe)
    
    return redirect(shoe.get_absolute_url())

@login_required
def delete_wishlist_item(request, item_id):
    item = get_object_or_404(models.WishlistItem, pk=item_id)

    #customers can only delete their own wishlist items
    if not ((hasattr(item.customer, 'user') and item.customer.user == request.user)):
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        item.delete()

    return redirect(reverse('products:wishlist'))

class WishlistView(LoginRequiredMixin,generic.ListView):
    model = models.WishlistItem
    template_name = 'products/wishlist.html'
    context_object_name = 'wishlist_items'
    paginate_by = 5
    
    def get_queryset(self):
        # base queryset already refers to WishlistItem objects
        qs = super().get_queryset().select_related('customer', 'shoe').prefetch_related('shoe__images')
        customer = self.request.user.customer_profile if self.request.user.is_authenticated else None
        if customer:
            # filter WishlistItem rows for this customer so template receives objects
            return qs.filter(customer=customer)
        return qs.none()

class ShoeDetailView(generic.DetailView):
    model = models.Shoe
    template_name = 'products/details.html'
    context_object_name = 'shoe'
    queryset = models.Shoe.objects.prefetch_related('images', 'variants')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        shoe = self.object

        # create dictionary for colour availability based on variant availability
        color_available = {}
        for color in shoe.variants.values_list('color', flat=True).distinct():
            color_variants = shoe.variants.filter(color=color)
            color_available[color] = any(variant.is_available for variant in color_variants)

        main_image = shoe.images.first()

        # get selected colour from query parameters
        selected_color = self.request.GET.get('color')
        # select the first if none selected
        if selected_color is None:
            selected_color = list(color_available.keys())[0]
        # get variants for the selected colour
        variants = shoe.variants.filter(color=selected_color).order_by('size') if selected_color else None

        context.update({
            'main_image': main_image,
            'color_available': color_available,
            'selected_color': selected_color,
            'variants': variants,
        })
        return context
    
class ShoeListView(generic.ListView):
    model = models.Shoe
    template_name = 'products/search.html'
    context_object_name = 'shoes'
    paginate_by = 6

    def get_queryset(self):
        # retrieve GET query parameters
        q = self.request.GET.get('q', '').strip() #keyword
        category = self.request.GET.get('category', '').strip()
        brand_id = self.request.GET.get('brand', '').strip()
        gender = self.request.GET.get('gender', '').strip()
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()

        #Get all objects with images
        qs = models.Shoe.objects.all().prefetch_related('images')

        #Build results queryset
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))

        if category:
            qs = qs.filter(category__iexact=category)

        if brand_id:
            brand_id = int(brand_id)
            qs = qs.filter(brand_id=brand_id)

        if gender:
            qs = qs.filter(gender__iexact=gender)

        if min_price:
            qs = qs.filter(price__gte=float(min_price))

        if max_price:
            qs = qs.filter(price__lte=float(max_price))

        return qs.order_by('price', 'name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # brands, genders and categories for dropdowns
        brands = models.Brand.objects.all().order_by('name')
        genders = models.Shoe.GENDER_CHOICES
        categories = models.Shoe.CATEGORY_CHOICES

        # keep original query strings
        q = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        brand = self.request.GET.get('brand', '').strip()
        gender = self.request.GET.get('gender', '').strip()
        min_price = self.request.GET.get('min_price', '').strip()
        max_price = self.request.GET.get('max_price', '').strip()

        context.update({
            'categories': categories,
            'brands': brands,
            'genders': genders,
            'q': q,
            'selected_category': category,
            'selected_gender': gender,
            'selected_brand': brand,
            'min_price': min_price,
            'max_price': max_price,
        })

        return context

class ShoeByGenderListView(ShoeListView):
    template_name = 'products/shoe_by_gender.html'

    def get_queryset(self):
        qs = super().get_queryset()
        gender = self.kwargs.get('gender', '').strip()
        return qs.filter(gender__iexact=gender) if gender else qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_gender = self.kwargs.get('gender', '').strip()
        selected_gender_label = models.Shoe.GENDER_CHOICES.get(selected_gender, '')
        if not selected_gender_label:
            raise Http404("Gender not found")
        context['selected_gender'] = selected_gender
        context['selected_gender_label'] = selected_gender_label
        # disable gender filter in search template
        context['rendered'] = 'shoe_by_gender'
        # Build breadcrumb
        breadcrumb = []
        # link to the gender listing
        
        category = self.request.GET.get('category', '').strip()
        if not category:
            breadcrumb.append({'title': selected_gender_label, 'url': None})
        else:
            gender_url = reverse('products:by_gender', args=[selected_gender])
            breadcrumb.append({'title': selected_gender_label, 'url': gender_url})
            category_label = models.Shoe.CATEGORY_CHOICES.get(category, category.title())
            # final breadcrumb item should be active (no url)
            breadcrumb.append({'title': category_label, 'url': None})

        context['breadcrumb'] = breadcrumb
        return context
    

class ShoeByBrandListView(ShoeListView):
    template_name = 'products/shoe_by_brand.html'

    def get_queryset(self):
        qs = super().get_queryset()
        brand_id = self.kwargs.get('brand_id', '')
        if not brand_id:
            return qs
        try:
            bid = int(brand_id)
            return qs.filter(pk=bid)
        except (ValueError, TypeError):
            return qs.filter(name__iexact=brand_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        brand_id = self.kwargs.get('brand_id', '')
        try:
            brand = models.Brand.objects.get(brand_id=brand_id)
        except (models.Brand.DoesNotExist, ValueError, TypeError):
            raise Http404('Brand not found')

        # selected_brand
        context['selected_brand'] = brand.brand_id
        context['selected_brand_obj'] = brand
        # disable the brand select
        context['rendered'] = 'shoe_by_brand'

        # Build breadcrumb
        breadcrumb = []

        category = self.request.GET.get('category', '').strip()
        if not category:
            breadcrumb.append({'title': brand.name, 'url': None})
        else:
            brand_url = reverse('products:by_brand', args=[brand.brand_id])
            breadcrumb.append({'title': brand.name, 'url': brand_url})

            category_label = models.Shoe.CATEGORY_CHOICES.get(category, category.title())
            # final breadcrumb item should be active (no url)
            breadcrumb.append({'title': category_label, 'url': None})
        
        context['breadcrumb'] = breadcrumb

        return context
    
    
def reviews(request,shoe_id):
    shoe = get_object_or_404(models.Shoe,shoe_id=shoe_id)
    reviews = models.Review.objects.filter(order_item__variant__shoe=shoe)
    avg_rating = reviews.aggregate(average=Avg('rating'))['average']
    # determine if the current user can leave a review: they must be authenticated
    # and have at least one Order with status 'Delivered' containing this shoe
    can_leave_review = False
    if request.user.is_authenticated:
        customer = getattr(request.user, 'customer_profile', None)
        if customer:
            delivered_orders = models.Order.objects.filter(customer=customer, status__iexact='delivered')
            if delivered_orders.exists():
                has_item = models.OrderItem.objects.filter(order__in=delivered_orders, variant__shoe=shoe).exists()
                can_leave_review = bool(has_item)

    context = {
        'shoe': shoe,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'can_leave_review': can_leave_review,
    }
    return render(request, 'products/reviews.html', context)

@login_required
def add_review(request, shoe_id):
    shoe = get_object_or_404(models.Shoe, shoe_id=shoe_id)

    order_item = None
    if request.user.is_authenticated:
        # pick the most recent delivered OrderItem
        order_item = (
            models.OrderItem.objects.filter(
                variant__shoe=shoe,
                order__customer__user=request.user,
                order__status__iexact='delivered'
            )
            .select_related('order', 'variant')
            .order_by('-order__delivery_date', '-order__order_date', '-pk')
            .first()
        )

    # Prevent users who haven't received the product from viewing the form
    if not order_item:
        return HttpResponseForbidden('You must purchase and receive the product before reviewing it.')

    # Prevent reviewing the same order_item more than once
    if models.Review.objects.filter(order_item=order_item).exists():
        return HttpResponseForbidden('This order item has already been reviewed.')

    if request.method == 'POST':
        form = Reviewform(request.POST, order_item=order_item, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            if not order_item:
                form.add_error(None, 'You must purchase and receive the product to review it.')
            else:
                review.order_item = order_item
                review.save()
                return redirect('products:reviews', shoe_id=shoe.shoe_id)
    else:
        form = Reviewform(order_item=order_item, user=request.user)

    context = {
        'shoe': shoe,
        'form': form,
    }
    return render(request, 'products/reviewform.html', context)


@login_required
def edit_review(request, review_id):
    review = get_object_or_404(models.Review, pk=review_id)

    # checks that the review belongs to logged-in customer first
    review_owner_user = getattr(review.order_item.order.customer, 'user', None)
    if review_owner_user != request.user:
        return HttpResponseForbidden('Not allowed')

    shoe = review.order_item.variant.shoe

    if request.method == 'POST':
        form = Reviewform(request.POST, instance=review, order_item=review.order_item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('products:reviews', shoe_id=shoe.shoe_id)
    else:
        form = Reviewform(instance=review, order_item=review.order_item, user=request.user)

    context = {
        'shoe': shoe,
        'form': form,
        'editing': True,
    }
    return render(request, 'products/reviewform.html', context)
