import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../core/theme/app_colors.dart';
import '../../widgets/custom_button.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Profile'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_rounded),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Avatar
          Center(
            child: Column(
              children: [
                Container(
                  width: 72, height: 72,
                  decoration: const BoxDecoration(
                    shape: BoxShape.circle,
                    color: AppColors.stone200,
                  ),
                  child: const Icon(Icons.person_rounded, size: 36, color: AppColors.stone500),
                ),
                const SizedBox(height: 12),
                Text('Your Profile',
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontFamily: GoogleFonts.playfairDisplay().fontFamily,
                    fontSize: 20,
                  ),
                ),
                const SizedBox(height: 4),
                Text('Manage your family health registry',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),

          const SizedBox(height: 28),
          const Divider(color: AppColors.stone200, thickness: 1.5),
          const SizedBox(height: 20),

          _Section(title: 'Family Registry', items: [
            _Item(icon: Icons.family_restroom_rounded, label: 'Register New Family',
              onTap: () => context.push('/register')),
            _Item(icon: Icons.list_alt_rounded, label: 'View Registered Families',
              onTap: () => context.push('/history')),
          ]),

          const SizedBox(height: 16),
          _Section(title: 'About', items: [
            _Item(icon: Icons.info_outline_rounded, label: 'About ArogyaLink', onTap: () {}),
            _Item(icon: Icons.phone_outlined, label: 'Emergency Number: 108', onTap: () {}),
            _Item(icon: Icons.code_rounded, label: 'Google Solution Challenge 2025', onTap: () {}),
          ]),

          const SizedBox(height: 28),
          CustomButton(
            label: 'Emergency Call',
            icon: Icons.phone_rounded,
            variant: BtnVariant.danger,
            fullWidth: true,
            onPressed: () => context.go('/'),
          ),
        ],
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final String title;
  final List<Widget> items;
  const _Section({required this.title, required this.items});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title.toUpperCase(),
          style: const TextStyle(
            fontSize: 10, fontWeight: FontWeight.w600,
            color: AppColors.stone400, letterSpacing: 1.5,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: AppColors.stone200, width: 1.5),
          ),
          child: Column(children: items),
        ),
      ],
    );
  }
}

class _Item extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _Item({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      leading: Icon(icon, color: AppColors.stone600, size: 20),
      title: Text(label, style: const TextStyle(fontSize: 14, color: AppColors.stone800)),
      trailing: const Icon(Icons.chevron_right_rounded, color: AppColors.stone400, size: 18),
      dense: true,
    );
  }
}
