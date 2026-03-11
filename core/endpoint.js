// Variables de entorno
const SKYMAVIS_API_KEY = process.env.SKYMAVIS_API_KEY;
const ENDPOINT_GRAPHQL = process.env.ENDPOINT_GRAPHQL;

const isEyesPart = (partId) => partId.includes("eyes");
const isEarsPart = (partId) => partId.includes("ears");

// ============================================
// Queries GraphQL
// ============================================
const GET_AXIE_DETAILS_QUERY = `query getAxieDetails($axieId: ID!) {
  axie(axieId: $axieId) {
    id
    name 
    class 
    stage
    owner  
    bodyShape 
    purity
    parts {
      id 
      name 
      class 
      type
      abilities {
        attack
        attackType
        backgroundUrl
        defense
        description
        effectIconUrl
        energy
        id
        name
      }
    }
    stats { hp morale skill speed }
    order { currentPriceUsd }
    transferHistory(from: 0, size: 50) {
      results { from to timestamp }
      total
    }
  }
}`;

const GET_WALLET_AXIES_QUERY = `query getWalletAxies($owner: String, $from: Int, $size: Int) {
  axies(owner: $owner, from: $from, size: $size, sort: IdAsc) {
    total
    results { id }
  }
}`;

const GET_SIMILAR_AXIES_QUERY = `query getSimilarAxies($from: Int, $size: Int, $criteria: AxieSearchCriteria) {
  axies(auctionType: Sale, sort: PriceAsc, from: $from, size: $size, criteria: $criteria) {
    total 
    results { id }
  }
}`;

// Métodos Base
// ============================================
const graphqlRequest = async (query, operationName, variables = {}) => {
  try {
    const response = await fetch(ENDPOINT_GRAPHQL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": SKYMAVIS_API_KEY,
      },
      body: JSON.stringify({ query, operationName, variables }),
    });

    const result = await response.json();
    if (result.errors) {
      console.error(
        `[GraphQL Error] en ${operationName}:`,
        JSON.stringify(result.errors, null, 2),
      );
      return null;
    }
    return result;
  } catch (error) {
    console.error(`[Network Error] en ${operationName}:`, error.message);
    return null;
  }
};

// Lógica de Negocio
// ============================================

const getAxieDetails = async (axieId) => {
  const response = await graphqlRequest(
    GET_AXIE_DETAILS_QUERY,
    "getAxieDetails",
    { axieId: String(axieId) },
  );
  return response?.data?.axie || null;
};

const getWalletAxies = async (walletId, from = 0, size = 50) => {
  const response = await graphqlRequest(
    GET_WALLET_AXIES_QUERY,
    "getWalletAxies",
    { owner: walletId, from, size },
  );

  if (!response?.data?.axies) return [[], 0];

  const total = response.data.axies.total;
  // Ejecutar peticiones de detalles en paralelo para velocidad
  const walletAxies = await Promise.all(
    response.data.axies.results.map((axie) => getAxieDetails(axie.id)),
  );

  return [walletAxies.filter((a) => a !== null), total];
};

const getSimilarAxiesRaw = async (criteria = {}, from = 0, size = 10) => {
  const response = await graphqlRequest(
    GET_SIMILAR_AXIES_QUERY,
    "getSimilarAxies",
    { from, size, criteria },
  );

  if (!response?.data?.axies) return [[], criteria, 0];

  const total = response.data.axies.total;
  const similarAxies = await Promise.all(
    response.data.axies.results.map((axie) => getAxieDetails(axie.id)),
  );

  return [similarAxies.filter((a) => a !== null), criteria, total];
};

// Orquestador de búsqueda recursiva/cascada
const getSimilarAxies = async (axie, from = 0, size = 10) => {
  const searchSteps = [
    () =>
      buildCriteria(axie, { useBodyShape: true, useClass: true, parts: "all" }),
    () =>
      buildCriteria(axie, {
        useBodyShape: false,
        useClass: true,
        parts: "all",
      }),
    () =>
      buildCriteria(axie, {
        useBodyShape: false,
        useClass: true,
        parts: "no-eyes",
      }),
    () =>
      buildCriteria(axie, {
        useBodyShape: false,
        useClass: true,
        parts: "no-ears",
      }),
    () =>
      buildCriteria(axie, {
        useBodyShape: false,
        useClass: true,
        parts: "no-eyes-ears",
      }),
    () =>
      buildCriteria(axie, {
        useBodyShape: false,
        useClass: false,
        parts: "no-eyes-ears",
      }),
  ];

  for (const step of searchSteps) {
    const criteria = step();
    const [axies, criteriaUsed, total] = await getSimilarAxiesRaw(
      criteria,
      from,
      size,
    );
    if (total > 0) return { axies, criteria: criteriaUsed, total };
  }

  return { axies: [], criteria: {}, total: 0 };
};

// Helper para construir el objeto Criteria correctamente
const buildCriteria = (axie, options) => {
  const criteria = {};

  if (options.useClass) criteria.classes = [axie.class];
  if (options.useBodyShape) criteria.bodyShapes = [axie.bodyShape];

  let parts = axie.parts.map((p) => p.id);

  if (options.parts === "no-eyes") parts = parts.filter((p) => !isEyesPart(p));
  if (options.parts === "no-ears") parts = parts.filter((p) => !isEarsPart(p));
  if (options.parts === "no-eyes-ears")
    parts = parts.filter((p) => !isEyesPart(p) && !isEarsPart(p));

  criteria.parts = parts;
  return criteria;
};

// ============================================
// CLI Handler
// ============================================
const handleCLI = async () => {
  const args = process.argv.slice(2);
  const command = args[0];

  try {
    if (command === "getAxieDetails") {
      console.log(JSON.stringify(await getAxieDetails(args[1])));
    } else if (command === "getWalletAxies") {
      const [axies, total] = await getWalletAxies(
        args[1],
        parseInt(args[2]),
        parseInt(args[3]),
      );
      console.log(JSON.stringify({ axies, total }));
    } else if (command === "getSimilarAxies") {
      const result = await getSimilarAxies(
        JSON.parse(args[1]),
        parseInt(args[2]),
        parseInt(args[3]),
      );
      console.log(JSON.stringify(result));
    }
  } catch (error) {
    console.error(JSON.stringify({ error: error.message }));
    process.exit(1);
  }
};

if (require.main === module) {
  handleCLI();
}

module.exports = { getAxieDetails, getWalletAxies, getSimilarAxies };



/*const test = async () => {
  console.log("--- Iniciando Prueba de Detalle ---");
  const axieId = "2957115";
  const wallet = "0xcdd08182476f178f422a16a6be7cff0a1243de6c";
  //const axieDetails = await getAxieDetails(axieId);
  const walletDetails = await getWalletAxies(wallet);

  if (walletDetails) {
    console.log("✅ Detalles:", walletDetails);
  } else {
    console.log(
      "❌ No se pudieron obtener los detalles. Revisa la consola para ver errores de red o GraphQL.",
    );
  }
};

test();*/