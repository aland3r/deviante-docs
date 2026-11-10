using System;
using System.Collections.Generic;

namespace DriftorDbFirst.Models;

public partial class Empresa
{
    public int Id { get; set; }

    public string Nome { get; set; }

    public string Cnpj { get; set; }

    public string Setor { get; set; }

    public virtual ICollection<Maquina> Maquinas { get; set; } = new List<Maquina>();
}
