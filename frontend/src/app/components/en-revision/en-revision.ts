import { Component, inject } from '@angular/core';
import { SesionService } from '../../services/sesion';
import { IconComponent } from '../icon/icon';

/** Lo que ve una cuenta nueva (rol "cliente") mientras un administrador revisa su solicitud. */
@Component({
  selector: 'app-en-revision',
  standalone: true,
  imports: [IconComponent],
  template: `
    <section class="caja">
      <span class="icono"><nt-icon name="inbox" [size]="22" /></span>
      @if (sesion.usuario()?.solicitud; as s) {
        @if (s.estado === 'pendiente') {
          <h1>Tu solicitud está en revisión</h1>
          <p>Pediste el rol de <strong>{{ s.rol_solicitado_display }}</strong>. Un administrador la revisará pronto;
            cuando la apruebe, este panel se transformará con las herramientas de tu rol.</p>
        } @else if (s.estado === 'rechazada') {
          <h1>Tu solicitud no fue aprobada</h1>
          <p>Pediste el rol de <strong>{{ s.rol_solicitado_display }}</strong>.@if (s.nota) { Nota del administrador: {{ s.nota }} }</p>
        } @else {
          <h1>¡Tu rol fue aprobado!</h1>
          <p>Cierra sesión y vuelve a entrar para ver tu panel.</p>
        }
      } @else {
        <h1>Tu cuenta no tiene un rol operativo</h1>
        <p>Puedes consultar la trazabilidad pública escaneando los códigos QR de los lotes.</p>
      }
      <p class="nota">La asignación de un rol no certifica oficialmente a la persona ni a su operación.</p>
    </section>
  `,
  styles: [`
    .caja { max-width: 560px; margin: 48px auto; text-align: center; background: var(--nt-crema); border: 1px solid var(--nt-borde); border-radius: 14px; padding: 36px 32px; }
    .icono { width: 52px; height: 52px; border-radius: 14px; background: var(--nt-menta); color: var(--nt-verde-900); display: inline-grid; place-items: center; }
    h1 { font-size: 22px; font-weight: 800; margin: 16px 0 8px; color: var(--nt-texto); }
    p { color: var(--nt-texto-suave); font-size: 14px; line-height: 1.6; }
    .nota { font-size: 12px; color: var(--nt-verde-500); margin: 18px 0 0; }
  `]
})
export class EnRevisionComponent {
  sesion = inject(SesionService);
}
