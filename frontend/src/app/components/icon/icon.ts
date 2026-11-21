import { Component, input } from '@angular/core';

export type NtIcon =
  | 'logo' | 'resumen' | 'lotes' | 'finca' | 'movimientos' | 'documentos'
  | 'bell' | 'plus' | 'search' | 'chevron' | 'arrow-up-right' | 'arrow-right'
  | 'download' | 'scan' | 'box' | 'warehouse' | 'shuffle' | 'clipboard'
  | 'info' | 'logout' | 'admin' | 'check' | 'eye' | 'lock' | 'calendar' | 'copy'
  | 'external' | 'pin' | 'close' | 'users' | 'shield' | 'inbox' | 'clock' | 'truck'
  | 'alert' | 'link' | 'refresh' | 'package-in' | 'package-out' | 'flag';

/** Íconos de trazo (24x24) usados en todo el panel del productor. */
@Component({
  selector: 'nt-icon',
  standalone: true,
  template: `
    <svg [attr.width]="size()" [attr.height]="size()" viewBox="0 0 24 24" fill="none"
         stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"
         aria-hidden="true">
      @switch (name()) {
        @case ('logo') { <path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.5 19 2c1 2 2 4.2 2 8 0 5.5-4.8 10-10 10Z"/><path d="M2 21c0-3 1.9-5.4 5-6 3-.6 5.5-2.3 7-5"/> }
        @case ('resumen') { <rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/> }
        @case ('lotes') { <path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5M12 13v8"/> }
        @case ('box') { <path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5M12 13v8"/> }
        @case ('finca') { <path d="M9 4 3 6v14l6-2 6 2 6-2V4l-6 2-6-2Z"/><path d="M9 4v14M15 6v14"/> }
        @case ('movimientos') { <path d="M17 3l4 4-4 4"/><path d="M3 7h18"/><path d="M7 21l-4-4 4-4"/><path d="M21 17H3"/> }
        @case ('shuffle') { <path d="M17 3l4 4-4 4"/><path d="M3 7h18"/><path d="M7 21l-4-4 4-4"/><path d="M21 17H3"/> }
        @case ('documentos') { <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z"/><path d="M14 3v5h5M9 13h6M9 17h6"/> }
        @case ('bell') { <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/> }
        @case ('plus') { <path d="M12 5v14M5 12h14"/> }
        @case ('search') { <circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/> }
        @case ('chevron') { <path d="m6 9 6 6 6-6"/> }
        @case ('arrow-up-right') { <path d="M7 17 17 7M8 7h9v9"/> }
        @case ('arrow-right') { <path d="M5 12h14M13 6l6 6-6 6"/> }
        @case ('download') { <path d="M12 3v12M7 10l5 5 5-5M4 21h16"/> }
        @case ('scan') { <path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/> }
        @case ('warehouse') { <path d="M3 21V9l9-5 9 5v12"/><path d="M7 21v-8h10v8M7 17h10"/> }
        @case ('clipboard') { <rect x="6" y="4" width="12" height="17" rx="2"/><path d="M9 4h6v3H9zM9 12h6M9 16h4"/> }
        @case ('info') { <circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/> }
        @case ('logout') { <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/> }
        @case ('check') { <path d="m5 12.5 4.5 4.5L19 7.5"/> }
        @case ('eye') { <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/> }
        @case ('lock') { <rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/> }
        @case ('calendar') { <rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/> }
        @case ('copy') { <rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15V5a2 2 0 0 1 2-2h8"/> }
        @case ('external') { <path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/> }
        @case ('pin') { <path d="M12 21s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12Z"/><circle cx="12" cy="9" r="2.5"/> }
        @case ('close') { <path d="M6 6l12 12M18 6 6 18"/> }
        @case ('users') { <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/> }
        @case ('shield') { <path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6l-8-3Z"/><path d="m9 12 2 2 4-4"/> }
        @case ('inbox') { <path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.5 5h13L22 12v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6l3.5-7Z"/> }
        @case ('clock') { <circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/> }
        @case ('truck') { <path d="M3 6h11v10H3zM14 9h4l3 3v4h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/> }
        @case ('alert') { <path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4M12 17h.01"/> }
        @case ('link') { <path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/> }
        @case ('refresh') { <path d="M21 12a9 9 0 0 1-15.5 6.2M3 12a9 9 0 0 1 15.5-6.2"/><path d="M21 4v5h-5M3 20v-5h5"/> }
        @case ('package-in') { <path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5"/><path d="M12 21v-8M9 16l3 3 3-3"/> }
        @case ('package-out') { <path d="M21 8 12 3 3 8v8l9 5 9-5V8Z"/><path d="m3 8 9 5 9-5"/><path d="M12 13v8M9 18l3-3 3 3"/> }
        @case ('flag') { <path d="M5 21V4M5 4h12l-2 4 2 4H5"/> }
        @case ('admin') { <path d="M12 3 4 6v6c0 5 3.4 8.4 8 9 4.6-.6 8-4 8-9V6l-8-3Z"/><path d="m9 12 2 2 4-4"/> }
      }
    </svg>
  `,
  styles: [`:host{display:inline-flex;line-height:0}`]
})
export class IconComponent {
  name = input.required<NtIcon>();
  size = input(18);
}
