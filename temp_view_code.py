
def register_tour_supplier(request):
    if request.method == 'POST':
        form = TourSupplierRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour Supplier registration successful! You can now login.')
            return redirect('login')
    else:
        form = TourSupplierRegistrationForm()
    
    return render(request, 'accounts/tour_supplier/register.html', {'form': form})
