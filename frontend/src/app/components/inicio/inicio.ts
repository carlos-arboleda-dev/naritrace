import { Component, inject } from '@angular/core';
import { SesionService } from '../../services/sesion';
import { ResumenComponent } from '../resumen/resumen';
import { AdminResumenComponent } from '../admin-resumen/admin-resumen';
import { DistribuidorResumenComponent } from '../distribuidor-resumen/distribuidor-resumen';
import { EnRevisionComponent } from '../en-revision/en-revision';

/** Pantalla de inicio de /dashboard/resumen: muestra el panel que corresponde al rol. */
@Component({
  selector: 'app-inicio',
  standalone: true,
  imports: [ResumenComponent, AdminResumenComponent, DistribuidorResumenComponent, EnRevisionComponent],
  template: `
    @if (sesion.cargado()) {
      @switch (sesion.grupo()) {
        @case ('productor') { <app-resumen /> }
        @case ('administrador') { <app-admin-resumen /> }
        @case ('distribuidor') { <app-distribuidor-resumen /> }
        @default { <app-en-revision /> }
      }
    }
  `
})
export class InicioComponent {
  sesion = inject(SesionService);
}
