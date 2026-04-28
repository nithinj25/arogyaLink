import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/theme/app_colors.dart';
import '../../widgets/emergency_button.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  Future<void> _callEmergency(BuildContext context) async {
    // In production: this dials the Twilio IVR number
    const number = '+15709815970'; // replace with actual IVR number
    final uri = Uri(scheme: 'tel', path: number);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    } else {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not place call. Check permissions.')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle.dark,
      child: Scaffold(
        backgroundColor: AppColors.background,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Column(
              children: [
                const SizedBox(height: 24),
                // Header
                Row(
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('ArogyaLink',
                          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                            fontFamily: GoogleFonts.playfairDisplay().fontFamily,
                          ),
                        ),
                        Text('Emergency Healthcare',
                          style: Theme.of(context).textTheme.bodySmall,
                        ),
                      ],
                    ),
                    const Spacer(),
                    IconButton(
                      onPressed: () => context.push('/history'),
                      icon: const Icon(Icons.history_rounded, color: AppColors.stone600),
                    ),
                    IconButton(
                      onPressed: () => context.push('/profile'),
                      icon: const Icon(Icons.person_outline_rounded, color: AppColors.stone600),
                    ),
                  ],
                ),

                const SizedBox(height: 20),
                const Divider(color: AppColors.stone200, thickness: 1.5, height: 0),
                const SizedBox(height: 48),

                // Emergency button
                EmergencyButton(onPressed: () => _callEmergency(context)),

                const SizedBox(height: 32),
                Text('Tap to call ArogyaLink emergency line',
                  style: Theme.of(context).textTheme.bodySmall,
                  textAlign: TextAlign.center,
                ),
                Text('Available 24/7 · Hindi, English, Kannada, Telugu',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.stone400,
                    fontSize: 11,
                  ),
                  textAlign: TextAlign.center,
                ),

                const Spacer(),

                // Quick actions
                Row(
                  children: [
                    Expanded(
                      child: _QuickAction(
                        icon: Icons.family_restroom_rounded,
                        label: 'Register\nFamily',
                        onTap: () => context.push('/register'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _QuickAction(
                        icon: Icons.history_rounded,
                        label: 'Call\nHistory',
                        onTap: () => context.push('/history'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _QuickAction(
                        icon: Icons.local_hospital_rounded,
                        label: 'Nearby\nPHC',
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('PHC locator coming soon')),
                          );
                        },
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 32),

                // Emergency info banner
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF2F2),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFFFECACA), width: 1.5),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.info_outline_rounded, color: AppColors.emergency, size: 18),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Text(
                          'For life-threatening emergencies, also call 108 (Ambulance) or 112 (National Emergency).',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: const Color(0xFF991B1B),
                            fontSize: 11,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  const _QuickAction({required this.icon, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppColors.stone200, width: 1.5),
        ),
        child: Column(
          children: [
            Icon(icon, color: AppColors.stone700, size: 22),
            const SizedBox(height: 6),
            Text(label,
              style: const TextStyle(fontSize: 11, color: AppColors.stone600, fontWeight: FontWeight.w500),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
