from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Sum, Q
from django.core.paginator import Paginator
from django.middleware.csrf import get_token
from Main.models import Modsinfo, Vehicle, ModCategory, Profile
from Main.forms import modform
from Users.forms import UserAdminForm, ProfileForm
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.core.files.base import ContentFile
import uuid,base64


def _style_admin_password_change_form(form):
    for field_name in ("password1", "password2"):
        field = form.fields.get(field_name)
        if field:
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} form-control".strip()
    return form

@staff_member_required
def admin_dashboard(request):
    # Stats
    total_mods = Modsinfo.objects.count()
    total_users = User.objects.count()
    total_downloads = Modsinfo.objects.aggregate(Sum('downloads'))['downloads__sum'] or 0
    total_likes = Modsinfo.objects.aggregate(Sum('likes'))['likes__sum'] or 0
    public_mods = Modsinfo.objects.filter(is_public=True).count()
    private_mods = Modsinfo.objects.filter(is_public=False).count()

    # Mods filters
    mod_search = request.GET.get('mod_search', '').strip()
    filter_type = request.GET.get('filter_type', '').strip()
    filter_category = request.GET.get('filter_category', '').strip()
    filter_visibility = request.GET.get('filter_visibility', '').strip()

    mods_qs = Modsinfo.objects.select_related('user', 'type', 'category').order_by('-uploaded_on')
    if mod_search:
        mods_qs = mods_qs.filter(Q(title__icontains=mod_search) | Q(user__username__icontains=mod_search))
    if filter_type:
        mods_qs = mods_qs.filter(type__id=filter_type)
    if filter_category:
        mods_qs = mods_qs.filter(category__id=filter_category)
    if filter_visibility == 'public':
        mods_qs = mods_qs.filter(is_public=True)
    elif filter_visibility == 'private':
        mods_qs = mods_qs.filter(is_public=False)

    mods_paginator = Paginator(mods_qs, 20)
    mods_page = mods_paginator.get_page(request.GET.get('page'))

    # Users filter
    user_search = request.GET.get('user_search', '').strip()
    users_qs = User.objects.select_related('profile').order_by('-date_joined')
    if user_search:
        users_qs = users_qs.filter(Q(username__icontains=user_search) | Q(email__icontains=user_search))

    users_paginator = Paginator(users_qs, 20)
    users_page = users_paginator.get_page(request.GET.get('page_u'))

    # Active tab
    active_tab = request.GET.get('tab', 'mods')
    if active_tab not in ('mods', 'users'):
        active_tab = 'mods'

    context = {
        'mods': mods_page,
        'users': users_page,
        'total_mods': total_mods,
        'total_users': total_users,
        'total_downloads': total_downloads,
        'total_likes': total_likes,
        'public_mods': public_mods,
        'private_mods': private_mods,
        'vehicle_types': Vehicle.objects.all(),
        'mod_categories': ModCategory.objects.all(),
        'mod_search': mod_search,
        'filter_type': filter_type,
        'filter_category': filter_category,
        'filter_visibility': filter_visibility,
        'user_search': user_search,
        'active_tab': active_tab,
    }
    return render(request, 'admin_panel/admin_panel.html', context)

@staff_member_required
def admin_toggle_visibility(request, mod_id):
    if request.method != 'POST':
        return HttpResponse(status=405)

    mod = get_object_or_404(Modsinfo, pk=mod_id)
    mod.is_public = not mod.is_public
    mod.save()

    csrf = get_token(request)
    css_class = 'bg-success text-white' if mod.is_public else 'bg-danger text-white'
    icon = '<i class="bi bi-globe me-1"></i>Public' if mod.is_public else '<i class="bi bi-lock-fill me-1"></i>Private'

    html = f"""
<span id="visibility-badge-{mod.id}">
    <form method="post"
          hx-post="/admin-panel/mod/{mod.id}/toggle-visibility/"
          hx-swap="outerHTML"
          hx-target="#visibility-badge-{mod.id}"
          style="display: inline;">
        <input type="hidden" name="csrfmiddlewaretoken" value="{csrf}">
        <button type="submit"
                class="badge border-0 {css_class}"
                style="cursor:pointer; font-size:0.75rem; padding:6px 12px; border-radius:50px; transition: all 0.2s;">
            {icon}
        </button>
    </form>
</span>"""
    return HttpResponse(html)

@staff_member_required
def admin_delete_mod(request, mod_id):
    mod = get_object_or_404(Modsinfo, pk=mod_id)
    mod_title = mod.title  # Save before delete

    default_thumb = 'img/default_placeholder.jpg'
    if mod.thumbnail_img and mod.thumbnail_img.name != default_thumb:
        mod.thumbnail_img.delete(save=False)
    for img_field in [mod.img_1, mod.img_2, mod.img_3]:
        if img_field and img_field.name != default_thumb:
            img_field.delete(save=False)

    mod.delete()
    messages.success(request, f"Mod '{mod_title}' has been deleted.")
    return redirect('admin_panel:admin_dashboard')

@staff_member_required
def admin_mod_edit(request, mod_id):
    mod = get_object_or_404(Modsinfo, pk=mod_id)
    if request.method == 'POST':
        form = modform(request.POST, request.FILES, instance=mod)
        if form.is_valid():
            form.save()
            messages.success(request, f'Mod "{mod.title}" updated successfully.')
            return redirect('admin_panel:admin_dashboard')
    else:
        form = modform(instance=mod)
    return render(request, 'admin_panel/admin_mod_edit.html', {'form': form})

@staff_member_required
def admin_mod_view(request, mod_id):
    mod = get_object_or_404(Modsinfo, pk=mod_id)
    return render(request, 'admin_panel/admin_mod_view.html', {'mod': mod})

@staff_member_required
def admin_mod_user_edit(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    profile, _ = Profile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        user_form = UserAdminForm(request.POST, instance=target_user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        user_form_valid = user_form.is_valid()
        profile_form_valid = profile_form.is_valid()

        if user_form_valid and profile_form_valid:
            # Save user
            updated_user = user_form.save(commit=False)
            updated_user.is_active = 'is_active' in request.POST
            updated_user.is_staff = 'is_staff' in request.POST
            updated_user.is_superuser = 'is_superuser' in request.POST
            updated_user.save()
            user_form.save_m2m()

            # Profile image
            cropped_data = request.POST.get('cropped_profile_image', '').strip()
            if cropped_data and cropped_data.startswith('data:image/'):
                fmt, imgstr = cropped_data.split(';base64,', 1)
                ext = fmt.split('/')[-1]
                filename = f"profile_{target_user.pk}_{uuid.uuid4().hex[:8]}.{ext}"
                profile.profile_image.save(filename, ContentFile(base64.b64decode(imgstr)), save=True)
            else:
                profile_form.save()

            messages.success(request, f'User "{target_user.username}" updated successfully.')
            return redirect('admin_panel:admin_dashboard')
        else:
            form_errors = f"User: {user_form.errors} | Profile: {profile_form.errors}"
            messages.error(request, f'Validation failed: {form_errors}')

    context = {
        'user': target_user,
        'profile': profile,
        'user_form': user_form if 'user_form' in locals() else UserAdminForm(instance=target_user),
        'profile_form': profile_form if 'profile_form' in locals() else ProfileForm(instance=profile),
        'user_form_errors': getattr(user_form, 'errors', None) if 'user_form' in locals() else None,
        'profile_form_errors': getattr(profile_form, 'errors', None) if 'profile_form' in locals() else None,
    }

    return render(request, 'admin_panel/admin_mod_user_edit.html', context)


@staff_member_required
def admin_mod_user_password(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    had_usable_password = target_user.has_usable_password()

    if request.method == 'POST':
        pwd_form = _style_admin_password_change_form(
            AdminPasswordChangeForm(target_user, request.POST)
        )
        if pwd_form.is_valid():
            pwd_form.save()
            if pwd_form.cleaned_data.get('set_usable_password'):
                if had_usable_password:
                    messages.success(
                        request,
                        f'Password updated successfully for "{target_user.username}".',
                    )
                else:
                    messages.success(
                        request,
                        f'Password-based authentication enabled for "{target_user.username}".',
                    )
            else:
                messages.success(
                    request,
                    f'Password-based authentication disabled for "{target_user.username}".',
                )
            return redirect('admin_panel:admin_mod_user_edit', user_id=target_user.pk)
    else:
        pwd_form = _style_admin_password_change_form(AdminPasswordChangeForm(target_user))

    context = {
        'target_user': target_user,
        'pwd_form': pwd_form,
        'show_usable_password_toggle': 'usable_password' in pwd_form.fields,
        'had_usable_password': had_usable_password,
    }
    return render(request, 'admin_panel/admin_mod_user_password.html', context)

@staff_member_required
def admin_delete_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if target_user.is_superuser:
        messages.error(request, "Superuser accounts cannot be deleted.")
        return redirect('admin_panel:admin_dashboard')

    if target_user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('admin_panel:admin_dashboard')

    username = target_user.username
    target_user.delete()
    messages.success(request, f"User '{username}' and all their mods have been deleted.")
    return redirect('admin_panel:admin_dashboard')
