import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { Grupo, SesionService, grupoDe } from '../services/sesion';

/** Deja pasar solo a los grupos indicados; sin sesión va al login, con otro rol al inicio. */
export const rolGuard = (...permitidos: Grupo[]): CanActivateFn => () => {
  const sesion = inject(SesionService);
  const router = inject(Router);
  return sesion.cargar().pipe(
    map(u => permitidos.includes(grupoDe(u.rol)) ? true : router.createUrlTree(['/dashboard/resumen'])),
    catchError(() => of(router.createUrlTree(['/login'])))
  );
};
